import numpy as np
R = 6371.0

def vectors(coords):
    c = np.radians(np.asarray(coords, dtype=float))
    a,b = c[...,0],c[...,1]
    return np.stack([np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)],axis=-1)

def angular(a,b):
    u,v = vectors(a),vectors(b)
    return np.degrees(np.arctan2(np.linalg.norm(np.cross(u,v),axis=-1),np.sum(u*v,axis=-1)))

def disk_samples(lat,lon,radius_km,count):
    i = np.arange(count)
    t = np.arccos(1-(i+.5)/count*(1-np.cos(radius_km/R)))
    az = i*np.pi*(3-np.sqrt(5))
    a,b = np.radians([lat,lon])
    lat2 = np.arcsin(np.sin(a)*np.cos(t)+np.cos(a)*np.sin(t)*np.cos(az))
    lon2 = b+np.arctan2(np.sin(az)*np.sin(t)*np.cos(a),np.cos(t)-np.sin(a)*np.sin(lat2))
    return np.column_stack([np.degrees(lat2),(np.degrees(lon2)+180)%360-180])

def uniform_point(rng):
    return np.array([np.degrees(np.arcsin(rng.uniform(-1,1))),rng.uniform(-180,180)])

def move(point, north, east):
    # Mutación sobre plano tangente: también es estable en los polos.
    a,b=np.radians(point)
    u=vectors(point)
    n=np.array([-np.sin(a)*np.cos(b),-np.sin(a)*np.sin(b),np.cos(a)])
    e=np.array([-np.sin(b),np.cos(b),0])
    v=u+np.radians(north)*n+np.radians(east)*e
    v/=np.linalg.norm(v)
    return np.array([np.degrees(np.arcsin(v[2])),np.degrees(np.arctan2(v[1],v[0]))])
