import asyncio, json, random, secrets, time
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(title='Martillazo y Gol - Beta completa')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
CARDS=json.loads((Path(__file__).parent/'players.json').read_text(encoding='utf-8'))
rooms={}; clients={}; locks={}
MAX_PARTICIPANTS=5
POSITIONS={'POR':1,'DEF':4,'MED':3,'DEL':3}

def ms():return int(time.time()*1000)
def eligible(card,slot):
 positions=card.get('positions') or []
 if slot in ('LI','LD','DFC'):return card.get('slotPosition')==slot or slot in positions or (slot=='DFC' and card.get('position')=='DEF' and not card.get('slotPosition'))
 if slot=='POR':return card['position']=='POR'
 if slot in ('MC','MCD'):return card['position']=='MED' and (slot in positions or card.get('slotPosition')==slot or not positions)
 return card['position']=='DEL' and (slot in positions or card.get('slotPosition')==slot)
SLOTS=['EI','DC','ED','MC','MCD','MC','LI','DFC','DFC','LD','POR']
def owned(p):return p['team']+p['bench']
def eleven(p):
 cards={c['id']:c for c in owned(p)}
 selected=[]
 for slot,cid in zip(SLOTS,p.get('lineup',[])):
  card=cards.get(cid)
  selected.append(card if card and eligible(card,slot) else None)
 return selected

def roster_valid(p):return all(eleven(p)) and len({c['id'] for c in eleven(p) if c})==11
def rank(room):
 rows=[]
 for p in room['players'].values():
  valid=roster_valid(p); rating=sum(c['rating'] for c in eleven(p) if c)
  rows.append(dict(id=p['id'],name=p['name'],score=rating,rating=rating,count=sum(c is not None for c in eleven(p)),valid=valid,budget=p['budget']))
 return sorted(rows,key=lambda x:(not x['valid'],-x['score'],-x['budget'],x['id']))

def public(room):
 cur=room['current']; settings=room['settings']
 return dict(code=room['code'],status=room['status'],host=room['host'],round=room['round'],totalRounds=settings['rounds'],settings=settings,
  players=[{k:v for k,v in p.items() if k!='token'} for p in room['players'].values()],visibility=room.get('visibility','private'),mode=room.get('mode','multi'),
  current=({'id':cur['id'],'base':0,'assetReady':cur['assetReady'],'silhouette':cur['silhouette']} if cur else None),
  reveal=room['reveal'],chat=room['chat'][-80:],endsAt=room['endsAt'],highest=room['highest'],leader=room['leader'],
  history=room['history'][-30:],results=room['results'],phase=room['phase'],offers=room.get('offers',[])[-100:])

async def notify(ws,message):await ws.send_json(dict(type='error',message=message))
async def broadcast(room):
 payload=dict(type='state',state=public(room),serverTime=ms())
 for sockets in list(clients.get(room['code'],{}).values()):
  for ws in list(sockets):
   try:await ws.send_json(payload)
   except Exception:sockets.discard(ws)

def auto_lineup(p):
 cards=owned(p);chosen=set();slots=[]
 for slot in SLOTS:
  options=[c for c in cards if c['id'] not in chosen and eligible(c,slot)]
  card=max(options,key=lambda c:c['rating']) if options else None
  slots.append(card['id'] if card else None)
  if card:chosen.add(card['id'])
 p['lineup']=slots

def complete_rosters(room):
 used={c['id'] for p in room['players'].values() for c in owned(p)}
 used.update(h['cardId'] for h in room['history'] if h.get('type')=='sold')
 for p in room['players'].values():
  auto_lineup(p)
  for index,slot in enumerate(SLOTS):
   if p['lineup'][index] is not None:continue
   options=[c for c in room['reserve'] if c['id'] not in used and eligible(c,slot)]
   if options:
    card=max(options,key=lambda c:c['rating']);p['bench'].append(card);used.add(card['id']);p['autoAssigned'].append(card['id']);auto_lineup(p)
 room['phase']='completion';room['results']=rank(room);room['status']='finished'

def make_deck(rounds):
 # Uniform random selection across all positions with available artwork.
 # Ensure each of the 11 formation slots has at least one chance to appear.
 pool=[c for c in CARDS if c.get('assetReady') and not c.get('reserveOnly')]
 if len(pool)<rounds:raise ValueError('No hay suficientes futbolistas preparados')
 selected=[];seen=set()
 for slot in SLOTS:
  choices=[c for c in pool if c['id'] not in seen and eligible(c,slot)]
  if choices:
   c=random.choice(choices);selected.append(c);seen.add(c['id'])
 others=[c for c in pool if c['id'] not in seen]
 selected+=random.sample(others,rounds-len(selected))
 random.shuffle(selected)
 return selected

def make_bot(room):
 token='bot-'+secrets.token_hex(5)
 room['players'][token]=dict(id=token,name='Martillo IA',budget=room['settings']['budget'],team=[],bench=[],lineup=[None]*11,autoAssigned=[],connected=True,ready=True,bot=True)
 return token

def next_round(room):
 room['round']+=1;room['leader']=None;room['highest']=0;room['reveal']=None
 if room['round']>room['settings']['rounds']:
  room['current']=None;room['endsAt']=None;complete_rosters(room);return
 room['current']=room['deck'][room['round']-1];room['endsAt']=ms()+room['settings']['duration']*1000;room['botNextAt']=ms()+random.randint(2500,6500)

async def clock(code):
 room=rooms[code]
 while room['status']=='auction' and code in rooms:
  await asyncio.sleep(.2)
  async with locks[code]:
   if room['status']!='auction':break
   if room['endsAt'] is None:continue
   # Bot bidding is server-authoritative and budget-limited.
   if room.get('mode')=='solo' and room['current'] and ms()>=room.get('botNextAt',0) and ms()<room['endsAt']-1800:
    room['botNextAt']=ms()+random.randint(3500,7000)
    bot=next((p for p in room['players'].values() if p.get('bot')),None)
    if bot and room['leader']!=bot['id'] and len(owned(bot))<14:
     minbid=room['highest']+1 if room['leader'] else 1
     wanted=any(eligible(room['current'],slot) and not eleven(bot)[i] for i,slot in enumerate(SLOTS))
     ceiling=min(bot['budget'],max(3,int(bot['budget']*.13)))
     if minbid<=ceiling and random.random()<(0.80 if wanted else 0.28):
      room['highest']=minbid+random.randint(0,min(2,ceiling-minbid));room['leader']=bot['id'];room['history'].append(dict(type='bid',winner=bot['name'],amount=room['highest']))
      room['endsAt']=max(room['endsAt'],ms()+5000);await broadcast(room)
   if ms()<room['endsAt']:continue
   card=room['current'];winner=room['players'].get(room['leader']) if room['leader'] else None
   if winner:
    winner['budget']-=room['highest']
    # Each manager can acquire reserves, but cannot take more than 11+3 cards.
    winner['bench'].append(card);auto_lineup(winner)
   room['history'].append(dict(type='sold' if winner else 'unsold',cardId=card['id'],player=card['name'],winner=winner['name'] if winner else None,amount=room['highest']))
   room['reveal']=dict(card=card,winner=winner['name'] if winner else None,amount=room['highest']);room['endsAt']=None
   await broadcast(room)
  await asyncio.sleep(6)
  async with locks[code]:
   if room['status']!='auction':break
   next_round(room);await broadcast(room)

@app.get('/health')
def health():return dict(ok=True,version='17.0',catalog=len(CARDS),readyAssets=sum(c.get('assetReady',False) for c in CARDS),rooms=len(rooms))

@app.get('/rooms')
def list_rooms():return public_rooms()

def public_rooms():return [dict(code=r['code'],players=len(r['players']),maxPlayers=MAX_PARTICIPANTS,settings=r['settings'],status=r['status']) for r in rooms.values() if r.get('visibility')=='public' and r['status']=='lobby' and len(r['players'])<MAX_PARTICIPANTS]

@app.websocket('/ws')
async def websocket(ws:WebSocket):
 await ws.accept();code=None;pid=None
 try:
  while True:
   data=await ws.receive_json();action=data.get('action')
   if action in ('create','join'):
    requested=str(data.get('code','')).strip().upper();token=str(data.get('token',''))[:100] or secrets.token_urlsafe(20)
    name=str(data.get('name','Manager')).strip()[:22] or 'Manager'
    if action=='create':
     visibility='public' if data.get('visibility')=='public' else 'private'
     mode='solo' if data.get('mode')=='solo' else 'multi'
     if mode=='solo':visibility='private'
     settings_in=data.get('settings') or {}
     try: duration=int(settings_in.get('duration',60));budget=int(settings_in.get('budget',500));rounds=int(settings_in.get('rounds',24))
     except (ValueError,TypeError):await notify(ws,'Configuración inválida');continue
     if not 15<=duration<=180 or not 1<=budget<=5000 or not 12<=rounds<=40:
      await notify(ws,'Duración 15-180s, presupuesto 1-5000M, rondas 12-40');continue
     code=secrets.token_hex(3).upper();deck=make_deck(rounds);deckids={c['id'] for c in deck}
     room=dict(code=code,status='lobby',host=token,round=0,players={},deck=deck,reserve=[c for c in CARDS if c['id'] not in deckids],current=None,highest=0,leader=None,endsAt=None,history=[],results=None,chat=[],reveal=None,phase='lobby',offers=[],offerSeq=0,settings=dict(duration=duration,budget=budget,rounds=rounds),visibility=visibility,mode=mode)
     rooms[code]=room;locks[code]=asyncio.Lock();clients[code]={}
     if mode=='solo':make_bot(room)
    else:
     code=requested;room=rooms.get(code)
     if not room:await notify(ws,'Sala no encontrada');code=None;continue
     if token.startswith('bot-'):await notify(ws,'La identidad de la IA no se puede utilizar');code=None;continue
     if room.get('mode')=='solo' and token not in room['players']:await notify(ws,'Esta sala es para un jugador y la IA');code=None;continue
    async with locks[code]:
     if token not in room['players']:
      if room['status']!='lobby' or len(room['players'])>=MAX_PARTICIPANTS:
       await notify(ws,'Sala iniciada o llena (máximo 5)');code=None;continue
      room['players'][token]=dict(id=token,name=name,budget=room['settings']['budget'],team=[],bench=[],lineup=[None]*11,autoAssigned=[],connected=True,ready=False)
     else:room['players'][token]['connected']=True
     pid=token;clients[code].setdefault(pid,set()).add(ws)
     await ws.send_json(dict(type='identity',token=pid,code=code));await broadcast(room)
   elif code and pid and code in rooms:
    room=rooms[code]
    async with locks[code]:
     if pid not in room['players']:await notify(ws,'Sesión inválida');continue
     p=room['players'][pid]
     if action=='leave':
      # Salida explícita: no equivale a una desconexión temporal.
      clients.get(code,{}).get(pid,set()).discard(ws)
      room['players'].pop(pid,None)
      for offer in room['offers']:
       if offer['status']=='pending' and pid in (offer['from'],offer['to']):offer['status']='cancelled'
      if room['host']==pid and room['players']:
       connected_members=[x for x in room['players'] if clients.get(code,{}).get(x)]
       room['host']=(connected_members or list(room['players']))[0]
       room['chat'].append(dict(name='Sistema',message='El anfitrión salió. Se asignó un nuevo anfitrión.',at=ms()))
      if room['leader']==pid:room['leader']=None;room['highest']=0
      await ws.send_json(dict(type='left'))
      if room['players']:await broadcast(room)
      else:
       rooms.pop(code,None);clients.pop(code,None);locks.pop(code,None)
      code=None;pid=None
      continue
     if action=='ready' and room['status']=='lobby':p['ready']=bool(data.get('ready'))
     elif action=='list_rooms':
      await ws.send_json(dict(type='rooms',rooms=public_rooms()))
      continue
     elif action=='start':
      if room['host']!=pid or room['status']!='lobby' or len(room['players'])<2 or not all(x['ready'] for x in room['players'].values()):
       await notify(ws,'Se necesitan 2-5 managers listos');continue
      room['status']='auction';room['phase']='main';next_round(room);asyncio.create_task(clock(code))
     elif action=='chat':
      msg=str(data.get('message','')).strip()[:240]
      if msg:room['chat'].append(dict(name=p['name'],message=msg,at=ms()))
     elif action=='restart':
      if room['host']!=pid or room['status']!='finished':await notify(ws,'Solo el anfitrión puede reiniciar');continue
      room.update(status='lobby',round=0,current=None,endsAt=None,leader=None,highest=0,reveal=None,results=None,history=[],phase='lobby',offers=[],offerSeq=0)
      room['deck']=make_deck(room['settings']['rounds']);used={c['id'] for c in room['deck']};room['reserve']=[c for c in CARDS if c['id'] not in used]
      for member in room['players'].values():member.update(budget=room['settings']['budget'],team=[],bench=[],lineup=[None]*11,autoAssigned=[],ready=False)
      room['chat'].append(dict(name='Sistema',message='Nueva partida lista. Marquen listo.',at=ms()))
     elif action=='lineup':
      if room['status'] not in ('auction','finished'):await notify(ws,'No se puede editar el once ahora');continue
      slot=data.get('slot');cid=data.get('cardId')
      if type(slot)!=int or not 0<=slot<11 or (cid is not None and type(cid)!=int):await notify(ws,'Posición inválida');continue
      card=next((c for c in owned(p) if c['id']==cid),None) if cid is not None else None
      if cid is not None and (not card or not eligible(card,SLOTS[slot])):await notify(ws,'La carta no es compatible con esa posición');continue
      lineup=p['lineup'];old= lineup[slot]
      if cid in lineup and cid is not None:lineup[lineup.index(cid)]=old
      lineup[slot]=cid
      if room['status']=='finished':room['results']=rank(room)
     elif action=='offer':
      if room['status'] not in ('auction','finished'):await notify(ws,'Mercado cerrado');continue
      target=data.get('to');kind=data.get('kind');give=data.get('give');receive=data.get('receive');cash=data.get('cash',0);payer=data.get('payer','from')
      if kind not in ('gift','sale','swap') or target==pid or target not in room['players'] or type(give)!=int or type(cash)!=int or cash<0 or payer not in ('from','to'):
       await notify(ws,'Propuesta inválida');continue
      other=room['players'][target]
      if not any(c['id']==give for c in owned(p)):await notify(ws,'No sos dueño de esa carta');continue
      if kind=='gift':receive=None;cash=0
      elif kind=='sale':receive=None;payer='to';
      elif kind=='swap' and (type(receive)!=int or not any(c['id']==receive for c in owned(other))):await notify(ws,'Elegí una carta del otro manager');continue
      if kind=='swap' and give==receive:await notify(ws,'Las cartas deben ser distintas');continue
      if cash>room['players'][payer if payer=='from' else target]['budget']:await notify(ws,'Presupuesto insuficiente');continue
      room['offerSeq']+=1;room['offers'].append(dict(id=room['offerSeq'],**{'from':pid},to=target,kind=kind,give=give,receive=receive,cash=cash,payer=payer,status='pending',at=ms()))
     elif action=='respond_offer':
      offer=next((x for x in room['offers'] if x['id']==data.get('offerId')),None)
      if not offer or offer['status']!='pending' or pid not in (offer['from'],offer['to']):await notify(ws,'Oferta no disponible');continue
      accept=data.get('accept') is True
      if not accept:offer['status']='rejected';await broadcast(room);continue
      if pid!=offer['to']:await notify(ws,'Solo el destinatario puede aceptar');continue
      sender=room['players'].get(offer['from']);recipient=room['players'].get(offer['to'])
      if not sender or not recipient:offer['status']='expired';await broadcast(room);continue
      give=next((c for c in owned(sender) if c['id']==offer['give']),None)
      receive=next((c for c in owned(recipient) if c['id']==offer['receive']),None) if offer['receive'] is not None else None
      paying=sender if offer['payer']=='from' else recipient
      if not give or (offer['kind']=='swap' and not receive) or paying['budget']<offer['cash']:
       offer['status']='expired';await notify(ws,'La oferta caducó: carta o presupuesto no disponible');await broadcast(room);continue
      def remove_card(member,card):
       member['team'][:]=[c for c in member['team'] if c['id']!=card['id']]
       member['bench'][:]=[c for c in member['bench'] if c['id']!=card['id']]
       member['lineup'][:]=[None if cid==card['id'] else cid for cid in member['lineup']]
      remove_card(sender,give);recipient['bench'].append(give)
      if receive:remove_card(recipient,receive);sender['bench'].append(receive)
      if offer['cash']:
       paying['budget']-=offer['cash'];(recipient if paying is sender else sender)['budget']+=offer['cash']
      auto_lineup(sender);auto_lineup(recipient);offer['status']='accepted'
      for other_offer in room['offers']:
       if other_offer['status']=='pending' and other_offer['id']!=offer['id'] and (other_offer['give'] in (give['id'],receive['id'] if receive else -1) or other_offer['receive'] in (give['id'],receive['id'] if receive else -1)):
        other_offer['status']='expired'
      room['chat'].append(dict(name='Sistema',message=f"Transferencia completada entre {sender['name']} y {recipient['name']}.",at=ms()))
      if room['status']=='finished':room['results']=rank(room)
     elif action=='bid':
      now=ms();amount=data.get('amount')
      if room['status']!='auction' or room['endsAt'] is None or now>=room['endsAt']:
       await notify(ws,'Ronda cerrada');continue
      minimum=1 if room['leader'] is None else room['highest']+1
      if type(amount)!=int or amount<minimum or amount>p['budget']:
       await notify(ws,f'Puja inválida: mínimo {minimum}M y máximo tu presupuesto');continue
      if room['leader']==pid or len(owned(p))>=14:
       await notify(ws,'Ya lideras o alcanzaste el límite de fichajes');continue
      room['highest']=amount;room['leader']=pid
      room['history'].append(dict(type='bid',winner=p['name'],amount=amount))
      room['endsAt']=max(room['endsAt'],now+5000)
     await broadcast(room)
   else:await notify(ws,'Primero crea o únete a una sala')
 except WebSocketDisconnect:pass
 finally:
  if code in rooms and pid and pid in rooms[code]['players']:
   async with locks[code]:
    clients.get(code,{}).get(pid,set()).discard(ws)
    if not clients.get(code,{}).get(pid):rooms[code]['players'][pid]['connected']=False
    await broadcast(rooms[code])
