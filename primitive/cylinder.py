import bpy
from math import pi, sin, cos, radians
from primitive.primitive import CreatePrimitive, PrimitiveGeometryClass
from bsmax.actions import delete_objects

def GetCylinderMesh(radius1, radius2, height, hsegs, csegs, ssegs, sliceon, sfrom, sto):
	verts,edges,faces = [],[],[]
	sides,heights = [],[]
	sfrom,sto = radians(sfrom),radians(sto)
	arcrange,slicestep,r1,r2 = pi*2, 0, radius1, radius2
	# height
	if sliceon:
		arcrange,slicestep = sto - sfrom, 1

	# collect segments x y onece
	for i in range(ssegs+slicestep):
		d = ((arcrange/ssegs)*i)+sfrom
		sides.append([sin(d),cos(d)])
	# collect cap arc height and scale
	for i in range(1,csegs):
		heights.append(cos(((pi/2)/csegs)*i))
	heights.reverse()

	# add one more step if sclise is on
	ssegs += slicestep
	# Create vertexes data
	step = (pi*2)/ssegs
	# first vertex
	if csegs > 1 or sliceon:
		verts.append([0,0,0])
	# lover part
	for i in range(csegs):
		s = (r1/csegs)*(i+1)
		for x, y in sides:
			verts.append([s*x,s*y,0])
	# Cylinder part
	h = height/hsegs
	rs = (r2-r1)/hsegs
	for i in range(1, hsegs):
		Z = h*i
		r = r1+rs*i
		for x, y in sides:
			verts.append([r*x, r*y, Z])
		if sliceon:
			for j in range(1, csegs):
				s = (r/csegs)*(csegs - j)
				X = s*x
				Y = s*y
			verts.append([0,0,Z]) # the center point
			# for j in range(1, csegs):
			# 	s = (r/csegs)*j
			# 	x, y = sides[0]
			# 	X = s*x
			# 	Y = s*y
	# uppaer part
	for i in range(csegs):
		s = (r2/csegs)*(csegs - i)
		for x, y in sides:
			verts.append([s*x, s*y, height])
	# last vertex
	if csegs > 1 or sliceon:
		verts.append([0,0,height])

	# Create Cap Faces
	if csegs == 1:
		cap = []
		if sliceon:
			for i in range(ssegs + 1):
				cap.append(i)
		else:
			for i in range(ssegs):
				cap.append(i)
		faces.append(cap)
	else:
		# First line
		for i in range(ssegs):
			faces.append([0,i, i + 1])
		if not sliceon:
			faces.append([0, ssegs, 1])

	# fill First cap
	for i in range(csegs - 1):
		s = ssegs * i
		if csegs > 1 or sliceon:
			s += 1
		for j in range(ssegs):
			a = s + j
			b = a + 1
			c = b + ssegs
			d = c - 1
			if j < ssegs - 1:
				faces.append((d, c, b, a))
			elif not sliceon:
				b = a - ssegs + 1
				c = d - ssegs + 1
				faces.append((d, c, b, a))
	# fill body
	f = (csegs - 1) * ssegs
	if csegs > 1 or sliceon:
		f += 1
	for i in range(hsegs):
		s = f + i * ssegs
		if sliceon and i > 0:
			s = f + i * (ssegs + 1) - 1
		for j in range(ssegs):
			a = s + j
			b = a + 1
			c = b + ssegs
			if sliceon and i > 0:
				c += 1
			d = c - 1
			if j < ssegs - 1:
				faces.append((d, c, b, a))
			elif not sliceon:
				b = a - ssegs + 1
				c = d - ssegs + 1
				faces.append((d, c, b, a))
	# fill upper cap
	# find firs vertex of upper cap
	f = hsegs * ssegs
	if csegs > 1:
		f += (csegs - 1) * ssegs + 1
	if sliceon:
		f += hsegs
		if csegs > 1:
			f -= 1
	# Create cap face
	if csegs == 1:
		cap = []
		if sliceon:
			for i in range(ssegs + 1):
				cap.append(f + i)
		else:
			for i in range(ssegs):
				cap.append(f + i)
		cap.reverse()
		faces.append(cap)

	for i in range(csegs - 1):
		s = f + ssegs * i
		for j in range(ssegs):
			a = s + j
			b = a + 1
			c = b + ssegs
			d = c - 1
			if j < ssegs - 1:
				faces.append((d, c, b, a))
			elif not sliceon:
				b = a - ssegs + 1
				c = d - ssegs + 1
				faces.append((d, c, b, a))
				
	# Fill last line
	if csegs > 1:
		l = len(verts) - 1
		f = l - ssegs
		for i in range(ssegs - 1):
			a = f + i
			b = a + 1
			faces.append([l, b, a])
		if not sliceon:
			faces.append([l, f, l - 1])

	# fill sliced face
	if sliceon:
		# Plate one
		cap = [0]
		for i in range(csegs + 1):
			cap.append(i * ssegs + 1)
		s = cap[-1]
		for i in range(1, hsegs):
			cap.append(s + i * (ssegs + 1))
		s = cap[-1]
		for i in range(1, csegs):
			cap.append(s + i * ssegs)
		cap.append(len(verts) - 1)
		s = csegs * ssegs + (hsegs - 1) * (ssegs + 1)
		for i in range(hsegs - 1):
			cap.append(s - i * (ssegs + 1))
		cap.reverse()
		faces.append(cap)
		# Plate two
		cap = [0]
		for i in range(csegs + 1):
			cap.append((i + 1) * ssegs)
		s = cap[-1]
		for i in range(1, hsegs):
			cap.append(s + i * (ssegs + 1))
		s = cap[-1]
		for i in range(1, csegs):
			cap.append(s + i * ssegs)
		cap.append(len(verts) - 1)
		s = csegs * ssegs + (hsegs - 1) * (ssegs + 1)
		for i in range(hsegs - 1):
			cap.append(s - i * (ssegs + 1))
		faces.append(cap)
	return verts, edges, faces

class Cylinder(PrimitiveGeometryClass):
	def __init__(self):
		self.classname = "Cylinder"
		self.finishon = 3
		self.owner = None
		self.data = None
	def reset(self):
		self.__init__()
	def create(self, ctx):
		mesh = GetCylinderMesh(0,0,0,1,1,18,False,0,360)
		self.create_mesh(ctx, mesh, self.classname)
		pd = self.data.primitivedata
		pd.classname = self.classname
		pd.hsegs, pd.csegs, pd.ssegs = 1, 1, 18
	def update(self):
		pd = self.data.primitivedata
		radius = pd.radius1
		mesh = GetCylinderMesh(radius, radius, pd.height, 
						pd.hsegs, pd.csegs, pd.ssegs,
						pd.sliceon, pd.sfrom, pd.sto)
		self.update_mesh(mesh)
	def abort(self):
		delete_objects([self.owner])

class Cone(PrimitiveGeometryClass):
	def __init__(self):
		self.classname = "Cone"
		self.finishon = 4
		self.owner = None
		self.data = None
	def reset(self):
		self.__init__()
	def create(self, ctx):
		mesh = GetCylinderMesh(0,0,0,1,1,18,False,0,360)
		self.create_mesh(ctx, mesh, self.classname)
		pd = self.data.primitivedata
		pd.classname = self.classname
		pd.hsegs, pd.csegs, pd.ssegs = 1, 1, 18
	def update(self):
		pd = self.data.primitivedata
		mesh = GetCylinderMesh(pd.radius1, pd.radius2, pd.height,
				pd.hsegs, pd.csegs, pd.ssegs,
				pd.sliceon, pd.sfrom, pd.sto)
		self.update_mesh(mesh)
		#self.data.use_auto_smooth = True
		#bpy.ops.object.shade_smooth() TODO find related data info
	def abort(self):
		delete_objects([self.owner])

class BsMax_OT_CreateCylinder(CreatePrimitive):
	bl_idname = "bsmax.createcylinder"
	bl_label = "Cylinder (Create)"
	subclass = Cylinder()

	def create(self, ctx, clickpoint):
		self.subclass.create(ctx)
		self.params = self.subclass.owner.data.primitivedata
		self.subclass.owner.location = clickpoint.view
		self.subclass.owner.rotation_euler = clickpoint.orient
	def update(self, clickcount, dimantion):
		if clickcount == 1:
			self.params.radius1 = dimantion.radius
		elif clickcount == 2:
			self.params.height = dimantion.height
		if clickcount > 0:
			self.subclass.update()
	def finish(self):
		pass

class BsMax_OT_CreateCone(CreatePrimitive):
	bl_idname = "bsmax.createcone"
	bl_label = "Cone (Create)"
	subclass = Cone()

	def create(self, ctx, clickpoint):
		self.subclass.create(ctx)
		self.params = self.subclass.owner.data.primitivedata
		self.subclass.owner.location = clickpoint.view
		self.subclass.owner.rotation_euler = clickpoint.orient
	def update(self, clickcount, dimantion):
		if clickcount == 1:
			self.params.radius1 = dimantion.radius
			self.params.radius2 = dimantion.radius
		elif clickcount == 2:
			self.params.height = dimantion.height
		elif clickcount == 3:
			radius2 = self.params.radius1 + dimantion.height_np
			self.params.radius2 = 0 if radius2 < 0 else radius2
		if clickcount > 0:
			self.subclass.update()
	def finish(self):
		pass

def cylinder_cls(register):
	classes = [BsMax_OT_CreateCylinder, BsMax_OT_CreateCone]
	for c in classes:
		if register: bpy.utils.register_class(c)
		else: bpy.utils.unregister_class(c)

if __name__ == '__main__':
	cylinder_cls(True)

__all__ = ["cylinder_cls", "Cylinder", "Cone"]