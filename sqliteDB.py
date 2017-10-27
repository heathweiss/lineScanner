import sqlite3
#conn = sqlite3.connect('lineScanner.db')

#c = conn.cursor()

def sayHello():
  print "hello from sqlite"

def getLayers(c):
  c.execute("select * from layer")
  return (c.fetchall())

def printLayers(layers):
  print layers

def insertLayer(layerName, x, y, z, conn, c):

  try:
    myId = getNextLayerId(c)
    
    c.execute("INSERT INTO layer VALUES (:myId, :layerName, :x, :y, :z)", {"myId": myId, "layerName": layerName, "x": x, "y": y, "z": z})
    conn.commit()

    print 'Layer has been inserted.'

  except sqlite3.IntegrityError:
    print "layer id already exists"

def getNextLayerId(c):
  c.execute("select count(*) from layer")
  if (c.fetchone()[0]) == 0:
    return 1
  else:
    c.execute("select max(id) from layer")
    return ((c.fetchone()[0]) + 1)

def getNextAngleHeightRadiusId(c):
  c.execute("select count(*) from angle_height_radius")
  if (c.fetchone()[0]) == 0:
    return 1
  else:
    c.execute("select max(id) from angle_height_radius")
    return ((c.fetchone()[0]) + 1)

#def getLayers():
#  c.execute("select * from layer")
#  return c.

def insertPoint(angle, height, radius, layerId, conn, c):

  try:
    #need to get the next available ID as sqlite does not create it.
    myId = getNextAngleHeightRadiusId(c)
    
    #need to confirm the id of the layer
    #allows foreign key for layer to be invalid. wtf?
    c.execute("INSERT INTO angle_height_radius VALUES (:myId, :angle, :height, :radius, :layerId)"
              , {"myId": myId, "angle": angle, "height": height, "radius": radius, "layerId": layerId})

    conn.commit()

    print 'Point has been inserted.'

  except sqlite3.IntegrityError:
    print "point id already exists"

#conn.close()


