## Resources
* [Information Extraction with Haystack and NuExtract](https://huggingface.co/learn/cookbook/en/information_extraction_haystack_nuextract)

## Query
```SQL
(
("Mexico City" OR CDMX OR "Ciudad de Mexico" OR "Ciudad de México")
AND
("will invest" OR "plans to invest" OR invested OR investing OR "investment of" OR capex OR "capital expenditure*" OR "to spend" OR spending OR build* OR construct* OR develop* OR expand* OR open* OR establish* OR "set up" OR inaugurate* OR "break ground" OR groundbreaking)
)
AND
(plant OR factory OR facility OR site OR campus OR warehouse* OR "distribution center*" OR "logistics hub*" OR datacent* OR "data center*" OR "centro de datos" OR laboratory OR lab OR "R&D" OR "research center" OR headquarters OR office)
AND
(USD OR MXN OR "US$" OR peso* OR dollar* OR million OR billion OR millon* OR millones OR "mdd" OR "mdp") NOT ( Fitch OR "Fitch Ratings" OR Moody* OR "Standard & Poor*" OR "S&P" OR DBRS OR rating* OR "credit rating" OR bond* OR note* OR "senior unsecured" OR "issuer default" OR IDR OR DSCR OR "country ceiling" OR coupon OR yield OR "tender offer" OR repurchase)
```
