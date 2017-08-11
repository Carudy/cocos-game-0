# -*- coding: utf-8 -*-
import os
import math
import cocos
import random
import cocos.euclid as eu
import cocos.collision_model as cm
import cocos.audio.pygame.mixer as mixer
import cocos.audio.pygame.music as music
import pyglet.image as pim
from cocos.actions import *

#************************************** Globals *************************************
_width,_height	=	1000,600
offset_x		=	0
map_w			=	0
map_now			=	[]
#************************************** defs *************************************
def get_ani(x):
	src='res/pics/ani/'+x+'_'
	re=[]
	for i in xrange(100):
		if os.path.exists(src+str(i)+'.png'):
			re.append(pim.load(src+str(i)+'.png'))
		else:
			return re
	return re
def cal_cd(x,y):
	return map(lambda i:i-min(i,y),x)
def cal_xy(x):
	global offset_x
	x.x=x.ox-offset_x
def get_map(x):
	global map_now
	map_now=[]
	cont=open('res/map/m'+str(x),'r').readlines()
	for i in cont:
		if len(i)>1:
			i=i.split(' ')
			map_now.append((int(i[0]),int(i[1]),int(i[2])+51))
def haiba(x):
	global map_now
	for i in map_now:
		if x>=i[0] and x<=i[1]:
			return i[2]
	return 0
def get_hid():
	now=1
	while 1:
		yield now
		now=(now+1)%100000
harm_id=get_hid()
def cal_rad(x,y):
	if x==0 and y==0:
		return 0
	du=180*math.acos(x/math.sqrt(x**2+y**2))/math.pi
	return du if y>0 else 360-du
def ch_xy(x,y):
	return x>0 and x<_width and y>0 and y<_height
#************************************** Classes *************************************
class Music():
	def __init__(self):	
		cocos.audio.pygame.mixer.init(22222,-16,2,1024*3)
		self.a=mixer.Sound('res/sound/v2.voc')
		self.a.set_volume(.5)
bgm=Music()
#************************************** Danmus *************************************
class Danmu_0(cocos.sprite.Sprite):			# danmu : line
	def __init__(self,img,x,y,drt,friend=1,speed=250,harm=1):
		super(Danmu_0,self).__init__('res/pics/danmu/'+img+'.png',position=(x,y))
		self.cshape = cm.CircleShape(eu.Vector2(self.x,self.y),self.width//2)
		self.friend,self.speed,self.harm=friend,speed,harm
		self.hid=harm_id.next()
		self.ox=self.x
		self.type=2
		self.t=0
		self.rotation=-drt
		drt*=math.pi/180
		self.dx,self.dy=speed*math.cos(drt),speed*math.sin(drt)
		self.schedule(self.run)
	def run(self,dt):		
		self.t+=dt
		self.ox+=self.dx*dt
		self.y+=self.dy*dt
		cal_xy(self)
		if self.t>3 or not ch_xy(self.x,self.y):
			self.kill()
		self.cshape.center = eu.Vector2(self.x,self.y)

class Danmu_circle(cocos.sprite.Sprite):		# danmu : a circle, n for all directions
	def __init__(self,img,x,y,n,rad=0,friend=1,speed=250,harm=1):
		super(Danmu_circle,self).__init__('res/pics/danmu/'+img+'.png',position=(x,y))
		self.du,self.img,self.rad=360.0/n,img,rad
		self.n,self.x,self.y,self.friend,self.speed,self.harm=n,x,y,friend,speed,harm
		self.type=3
		self.schedule(self.run)
		self.visible=0
	def run(self,dt):
		for i in xrange(self.n):
			self.parent.add(Danmu_0(self.img,self.x,self.y,self.rad+self.du*i,self.friend,self.speed,self.harm))
		self.kill()

class Danmu_kenshin(cocos.sprite.Sprite):		# Jian Shen
	def __init__(self,img,x,y,n,friend=0,speed=350,harm=1):
		super(Danmu_kenshin,self).__init__('res/pics/danmu/'+img+'.png',position=(x,y))
		self.type=3
		self.n,self.x,self.y,self.friend,self.speed,self.harm=n,x,y,friend,speed,harm
		self.img,self.cd,self.t,self.du=img,0,0,0
		self.schedule(self.run)
		self.visible=0
	def run(self,dt):
		self.t+=dt
		self.cd-=dt
		if self.cd<=0:
			self.cd=0.1
			self.parent.add(Danmu_circle(self.img,self.x,self.y,self.n,self.du,self.friend,self.speed,self.harm))
			self.du+=5 if self.t<1.5 else -10
		if self.t>4.5:
			self.kill()

class Danmu_goken(cocos.sprite.Sprite):			# Yu Jian Shu
	def __init__(self,img,x,y,friend=0,speed=500,harm=1):
		super(Danmu_goken,self).__init__('res/pics/danmu/'+img+'.png',position=(x,y))
		self.type=3
		self.x,self.y,self.friend,self.speed,self.harm=x,y,friend,speed,harm
		self.img,self.cd,self.t=img,0,0
		self.schedule(self.run)
		self.rotation=-135
		self.do(RotateTo(45,0.5))
		self.cshape = cm.CircleShape(eu.Vector2(self.x,self.y),self.width//2)
	def run(self,dt):
		global offset_x
		self.t+=dt
		self.cd-=dt
		if self.t>0.5:
			self.visible=0
			if self.cd<=0:
				self.cd=0.08
				x=self.x+offset_x+random.choice(range(100))-50
				y=self.y+random.choice(range(100))-50
				fx,spd=(1,-0.6),800
				if len(self.parent.eners):
					for i in self.parent.coli[1].ranked_objs_near(self,600):
						if i[0].type==1:
							fx=(i[0].x-x,i[0].y-y)
							spd=min(spd,i[1]*10)
							break
				spd=max(spd,400)
				self.parent.add(Danmu_0(self.img,x,y,cal_rad(fx[0],fx[1]),self.friend,spd,self.harm))
		if self.t>1:
			self.kill()

#************************************** Sprites *************************************
class Ziji(cocos.sprite.Sprite):
	def __init__(self):
		self.acts=[get_ani('stand'),get_ani('jmp'),get_ani('atk'),get_ani('jatk')]
		self.acts+=[get_ani('walk')]
		super(Ziji,self).__init__(self.acts[0][0],position=(400,300))
		self.type,self.friend=0,0
		self.ori=self.image
		self.speed,self.direction=300,1
		self.dx,self.dy=0,0
		self.schedule(self.run)
		self.cshape = cm.CircleShape(eu.Vector2(self.x,self.y),self.width//2)
		self.atking,self.jmping,self.magicing=0,0,0
		self.status,self.pt,self.next_sta=0,0,0
		self.cds=[0]*10
		self.magic=['i']

	def do_move(self,dt):
		global keym,offset_x,map_w,_width
		self.scale_x=self.direction
		self.direction=self.dx if self.dx else self.direction
		kv=0.1 if self.status in [2,3] else 1
		dx=self.speed*self.dx*dt*(0.5 if self.jmping else 1)*kv
		dy=self.speed*self.dy*dt*kv
		if haiba(self.x+dx+offset_x)>self.y+self.dy:
			dx=0
		self.x+=dx
		self.y+=dy
		if self.x>750 and _width+offset_x+250<map_w:
			offset_x+=self.x-750
			self.x=750
		elif self.x<250 and offset_x>0:
			offset_x+=self.x-250
			self.x=250
		self.x=max(5,self.x)
		self.x=min(_width-5,self.x)
		self.cshape.center = eu.Vector2(self.x,self.y)

	def cal_sta(self,dt):
		global keym
		if self.jmping:
			if self.atking:
				self.next_sta=3
			else:
				self.next_sta=1
		else:
			if self.atking:
				self.next_sta=2
			else:
				self.next_sta=4 if self.dx else 0
		if self.next_sta!=self.status and (self.status==4 or self.pt==len(self.acts[self.status])-1):
			self.status,self.pt,self.cds[0]=self.next_sta,0,0.05
			self.image=self.acts[self.status][0]
		if len(self.acts[self.status])>1:
			if self.cds[0]<=0:
				self.cds[0]=0.08
				self.pt=(self.pt+1)%(len(self.acts[self.status]))
		self.image=self.acts[self.status][self.pt]

	def cal_km(self,dt):
		global bgm,offset_x
		for i in self.magic:
			if ord(i) in keym.keyp and self.cds[1]<=0:
				self.cds[1]=1
				self.parent.add(Danmu_goken('dan1',self.x+70*self.direction,self.y+140))
				bgm.a.play()
				self.magicing=1
				self.atking=0
				self.dx=0
				return
		self.atking=ord('j') in keym.keyp
		if not self.atking:
			self.dx=(1 if ord('d') in keym.keyp else -1 if ord('a') in keym.keyp else 0)
			if ord('k') in keym.keyp and not self.jmping:
				self.dy=4.5

	def run(self,dt):
		self.cds=cal_cd(self.cds,dt)
		self.cal_km(dt)
		self.cal_sta(dt)
		self.do_move(dt)
		

class Diji(cocos.sprite.Sprite):
	def __init__(self):
		super(Diji,self).__init__('res/pics/zl.png',position=(500,400))
		self.cshape = cm.CircleShape(eu.Vector2(self.x,self.y),self.width//2)
		self.type,self.friend=1,1
		self.do(MoveBy((0,-200),0.5))
		self.schedule(self.run)
		self.ox=self.x
		self.harm_s=set()
		self.life=100

	def get_harm(self,x,y):
		if x in self.harm_s:
			return
		self.harm_s.add(x)
		self.life-=y
		if self.life<0:
			self.kill()

	def run(self,dt):
		cal_xy(self)
		self.cshape.center = eu.Vector2(self.x,self.y)

#************************************** Bks *************************************
class Bk0(cocos.sprite.Sprite):
	def __init__(self):
		global map_w
		super(Bk0,self).__init__('res/pics/bk/bk0.jpg')
		map_w=self.width
		self.position=_width//2,_height//2
		self.ox=self.x
		get_map(0)
		self.schedule(self.run)
	def run(self,dt):
		cal_xy(self)
#************************************** Layers *************************************
class Key_Mouse(cocos.layer.Layer):
	is_event_handler = True
	def __init__(self):
		super(Key_Mouse,self).__init__()
		self.keyp=set()
	def on_key_press (self,key,modifiers):
		self.keyp.add(key)
	def on_key_release (self,key,modifiers):
		self.keyp.remove(key)

class L0(cocos.layer.Layer):
	def __init__(self):
		super(L0,self).__init__()
		self.add(Bk0())

class L1(cocos.layer.Layer):
	def __init__(self):
		super(L1,self).__init__()
		self.dy,self.zl=Ziji(),Diji()
		self.add(self.dy)
		self.add(self.zl)
		self.coli=[cm.CollisionManagerBruteForce(),cm.CollisionManagerBruteForce()]
		self.eners=[]
		self.schedule(self.run)

	def deal_harm(self,x):
		for i in x.known_objs():
			if i.type==0 or i.type==1:
				for j in x.iter_colliding(i):
					if j.type==2:
						i.get_harm(j.hid,j.harm)

	def deal_coli(self):
		self.coli[0].clear()		# colis for ziji and allies 
		self.coli[1].clear()		# colis for enermies
		self.coli[0].add(self.dy)
		self.eners=[]
		for i in self.get_children():
			if i.type!=3 and i.type!=0:
				self.coli[(i.type-1)^i.friend].add(i)
				if i.type==1 and i.friend==1:
					self.eners.append(i)

	def deal_gravity(self,dt):
		floor=haiba(self.dy.x+offset_x)
		if self.dy.y>floor:
			self.dy.dy-=dt*9
			self.dy.jmping=1
			self.dy.y-=min(self.dy.y-floor,4)
		else:
			self.dy.jmping=0
			self.dy.dy=0
			self.dy.y=floor

	def run(self,dt):
		self.deal_coli()
		self.deal_harm(self.coli[0])
		self.deal_harm(self.coli[1])
		self.deal_gravity(dt)


#************************************** Mains *************************************
cocos.director.director.init(width=_width,height=_height,caption="game")
keym=Key_Mouse()
s1=cocos.scene.Scene(keym,L0(),L1())
cocos.director.director.run(s1)
