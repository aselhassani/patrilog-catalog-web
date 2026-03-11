import urllib.request, json

url = 'https://patrilog.com/api/getLots.php?filter_surface=[0,1500]&filter_type=all&filter_destination=all'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read())

habitat = [l for l in data if l.get('destination','') == 'Habitat' and l.get('prix_total',0) > 0 and l.get('surf',0) > 0]
commerce = [l for l in data if 'commercial' in l.get('destination','').lower() and l.get('prix_total',0) > 0 and l.get('surf',0) > 0]

avg_h = sum(l['prix_total']/l['surf'] for l in habitat) / len(habitat) if habitat else 0
avg_c = sum(l['prix_total']/l['surf'] for l in commerce) / len(commerce) if commerce else 0

print(f'=== ANALYSE DES DONNEES ===')
print(f'Lots Habitat avec prix: {len(habitat)}')
print(f'Lots Commerce avec prix: {len(commerce)}')
print()
print(f'Prix moyen/m2 Habitat:  {avg_h:,.0f} DH')
print(f'Prix moyen/m2 Commerce: {avg_c:,.0f} DH')
print(f'Ratio Commerce/Habitat: {avg_c/avg_h:.2f}x')
print()

indices_h = sorted([l['prix_total']/l['surf']/avg_h for l in habitat])
indices_c = sorted([l['prix_total']/l['surf']/avg_c for l in commerce])

print('=== INDICES HABITAT (sans majoration) ===')
print(f'  Min:    {indices_h[0]:.3f}')
print(f'  Q1:     {indices_h[len(indices_h)//4]:.3f}')
print(f'  Median: {indices_h[len(indices_h)//2]:.3f}')
print(f'  Q3:     {indices_h[3*len(indices_h)//4]:.3f}')
print(f'  Max:    {indices_h[-1]:.3f}')

print()
print('=== INDICES COMMERCE (sans majoration) ===')
print(f'  Min:    {indices_c[0]:.3f}')
print(f'  Q1:     {indices_c[len(indices_c)//4]:.3f}')
print(f'  Median: {indices_c[len(indices_c)//2]:.3f}')
print(f'  Q3:     {indices_c[3*len(indices_c)//4]:.3f}')
print(f'  Max:    {indices_c[-1]:.3f}')

print()
print('=== CE QUE SIGNIFIE LE COEFFICIENT ===')
print(f'  Sans coef: un lot commerce a indice=1.000 = prix/m2 dans la moyenne commerce')
print(f'  Avec 1.10: ce meme lot passe a indice=1.100')
print(f'  => Il faut que le lot commerce soit 10% moins cher/m2 que sa moyenne')
print(f'     pour etre au meme niveau qu un lot habitat moyen (indice=1.0)')
print()

print('=== IMPACT DU COEFFICIENT SUR LE CLASSEMENT MIXTE ===')
for coef in [1.0, 1.05, 1.1, 1.15, 1.2, 1.3]:
    all_indices = [(i, 'H') for i in indices_h] + [(i * coef, 'C') for i in indices_c]
    all_indices.sort(key=lambda x: x[0])
    top10 = all_indices[:10]
    nb_c_top10 = sum(1 for _, t in top10 if t == 'C')
    top20 = all_indices[:20]
    nb_c_top20 = sum(1 for _, t in top20 if t == 'C')
    print(f'  Coef {coef:.2f}: Commerce dans top10={nb_c_top10}, top20={nb_c_top20}')
