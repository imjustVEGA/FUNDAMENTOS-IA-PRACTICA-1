import numpy as np
from .app.domain.sphere_geometry import R_TIERRA_KM, destinos_geodesicos
R = R_TIERRA_KM

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
    return destinos_geodesicos(lat, lon, t, az)

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
