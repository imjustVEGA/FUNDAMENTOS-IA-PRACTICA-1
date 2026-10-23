from .models import Scenario, Region, Zone

def base_scenario() -> Scenario:
    return Scenario(regions=[Region(name=n, lat=a, lon=b, weight=w) for n,a,b,w in [
        ('Península de Yucatán',20.5,-89,3),('Amazonía brasileña',-3.5,-62,3),
        ('California',36.8,-119.4,2),('Sahel',15,0,2),('Japón',36,138,2),
        ('Interior de Australia',-25,133,1)]], zones=[
        Zone(name='Atlántico Norte',lat=45,lon=-35,radius_deg=12),
        Zone(name='Pacífico Sur',lat=-30,lon=-120,radius_deg=10),
        Zone(name='Polar norte',lat=78,lon=30,radius_deg=8),
        Zone(name='Objeto A',lat=10,lon=45,radius_deg=5,kind='object'),
        Zone(name='Objeto B',lat=-15,lon=110,radius_deg=5,kind='object')])
