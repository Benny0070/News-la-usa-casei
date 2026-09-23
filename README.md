# Rezumatul zilei

Pagină de știri personală, independentă de Claude: titluri, link direct către
sursă și rezumat în română, filtrabile pe domenii de interes. Se actualizează
singură în fiecare dimineață, gratuit, prin GitHub Actions + GitHub Pages.

## Ce face

- `fetch_news.py` ia zilnic titluri din Google News RSS pentru 6 domenii
  (politică România, economie/business, tehnologie, internațional, sport,
  politică mondială), traduce în română ce e în engleză, și scrie totul în
  `news.json`.
- `index.html` citește `news.json` și afișează știrile: căutare, filtrare pe
  domenii (se ține minte alegerea ta, local, în telefon/browser), link direct
  la articol, buton de rezumat în română.
- `.github/workflows/update-news.yml` rulează scriptul automat în fiecare zi
  la 05:00 UTC (~07:00–08:00 ora României) și publică rezultatul.

## Instalare (10 minute, o singură dată)

1. **Cont GitHub** — dacă nu ai deja, creează unul gratuit pe github.com.
2. **Repo nou** — apasă "New repository", dă-i un nume (ex: `stiri-zilnice`),
   lasă-l **Public** (necesar pentru Pages + Actions gratuit), fără README
   (îl ai deja aici).
3. **Încarcă fișierele** — cel mai simplu: pe pagina repo-ului nou, "Add file"
   → "Upload files", și tragi acolo toate fișierele din acest folder
   (inclusiv folderul `.github`, cu tot cu subfolderul `workflows`).
   Alternativ, dacă folosești `git` de pe calculator:
   ```
   cd stiri-zilnice
   git init
   git add .
   git commit -m "Prima versiune"
   git branch -M main
   git remote add origin https://github.com/NUME_UTILIZATOR/stiri-zilnice.git
   git push -u origin main
   ```
4. **Activează GitHub Pages** — în repo, Settings → Pages → sub "Build and
   deployment", la "Source" alege **"Deploy from a branch"**, branch `main`,
   folder `/ (root)`, apoi Save. După 1-2 minute, pagina ta va fi vie la:
   `https://NUME_UTILIZATOR.github.io/stiri-zilnice/`
5. **Rulează prima actualizare manual** — în repo, tab "Actions" → selectezi
   workflow-ul "Actualizeaza stirile" → "Run workflow" → Run workflow. După
   circa un minut, va apărea un commit nou cu `news.json` completat.
6. **Deschide link-ul pe telefon/iPad** — adaugă-l ca shortcut pe ecranul
   principal (Share → "Add to Home Screen"), și arată exact ca o aplicație.

De atunci încolo, în fiecare dimineață pagina se reînnoiește singură — nu mai
trebuie să faci nimic.

## Cum personalizezi domeniile

Deschide `fetch_news.py` și editează dicționarul `FEEDS` de la început:
schimbă textul din `q=...` (interogarea de căutare) sau adaugă/șterge
categorii întregi. Fiecare intrare are nevoie de un `label` (numele afișat)
și un `url` (feed-ul RSS). După ce salvezi și încarci modificarea pe GitHub,
următoarea rulare automată (sau una manuală, din Actions) va folosi noile
domenii — categoriile noi apar automat și ca butoane de filtrare în pagină.

## Limitări de care să știi

- Traducerea folosește un serviciu gratuit (Google Translate, prin pachetul
  `deep-translator`), nu un model AI — deci "rezumatul" e o traducere a
  scurtei descrieri din RSS, nu un rezumat inteligent generat de o IA. E
  suficient de bun pentru a înțelege rapid despre ce e vorba, dar nu
  înlocuiește articolul.
- Sursele vin din Google News RSS, care agregă din mai multe publicații —
  n-ai control fin peste care ziar anume apare pentru fiecare știre.
- GitHub Actions e gratuit nelimitat pentru repo-uri publice; dacă preferi
  un repo privat, ai un buget lunar gratuit de minute care e oricum mult
  peste ce consumă o rulare zilnică de un minut.
