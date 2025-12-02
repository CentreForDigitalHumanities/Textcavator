De database waar Textcavator mee werkt is georganiseerd met Elasticsearch. Om daarin te zoeken, is het nodig termen en operatoren te gebruiken, die Elasticsearch “begrijpt”. Deze worden uitgebreid uitgelegd in de [Simple Query String-handleiding van Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/query-dsl-simple-query-string-query.html#simple-query-string-syntax).

Hieronder volgt een beschrijving van de ondersteunde operatoren.

# Simple Query String syntax

Deze zoekmethode ondersteunt de volgende functies:

| Functie | Beschrijving |
|:---:| --- |
| `+` | staat voor AND (bank AND kapitaal) |
| &#124; | staat voor OR (bank OR kapitaal) |
| `-` | betekent bevat niet (niet kapitaal) |
| `"` | maakt het mogelijk op een complete frase tegelijk te zoeken “het kapitaal van de bank” |
| `*` | is alleen toegestaan na een aantal andere karakters en is een wildcard voor een aantal letters (`kapit*` is toegestaan `*kapit` niet) |
| `~N` | na een woord betekent woord + willekeurige letters (fuzziness), geef hier het aantal willekeurige letters dat anders mag zijn. Dus `bank~1` zoekt ook balk, blak, dank enz. |
| `~N` | na een frase van enkele woorden geeft aan hoeveel woorden anders mogen zijn |

Tekens zoals `|` en `+`, zijn gereserveerde karakters. Wilt u zoeken op woorden die juist zulke tekens bevatten, dan moet het teken worden voorafgegaan door `\`.

De zoekfunctie staat default ingesteld op `OR`. Dat betekent dat als u intypt: `Plaat Fiets`, er wordt gezocht op of documenten die `Plaat` of documenten die `Fiets` bevatten. Dit heeft ook consequenties voor de `–`functie. `Plaat Fiets –Tafel` wordt: documenten die `Plaat` bevatten of documenten die `Fiets` bevatten of documenten die niet het woord `Tafel` bevatten.

## Pas op de spatie
Een spatie kan ook een speciaal teken zijn. Soms kan een escape (dus `\`) voor de spatie nodig zijn.

### Voorbeelden van zoekresultaten

> Vraag: termen kapitaal en bank in alle velden in verschillende combinaties

| Zoekterm | Treffers |
| --- | --- |
| `kapitaal` | 568 treffers |
| `bank` | 76161 treffers |
| `bank  +kapitaal` |		256 treffers  (bank EN kapitaal)|
| `+bank +kapitaal` |		256 treffers (EN bank En kapitaal)|
| `+bank +-kapitaal` |	75905 treffers (bank en niet kapitaal ofwel documenten waar bank wel in voorkomt en documenten waar kapitaal niet in voorkomt) |
| `+-bank+kapitaal`|		312 treffers (niet bank maar wel kapitaal) |
| `"kapitaal van de bank"` |	2 treffers|
| `kapitaal deposito` |		632 treffers|
| `kapitaaldeposito`|  		2 treffers|
| `+kapitaal +deposito`|		27 treffers|
| `kapitaaldeposito~1` |		2 treffers|
| `kapitaaldeposito~2` |	4 treffers waarvan 2 maal kapitaaldeposito’s (2 tekens verschil) |
| `kapit*`|			910 treffers |
| `*kapit` |				There were no results to your query. |
| `bank~1` | 			76241 treffers (vergelijk met bank hiervoor) |
| `"de bank is"` |  			24 treffers |
| `"de bank is" ~1`|		32 treffers  |
