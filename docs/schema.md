---
langs: [en, nb-NO]
lastUpdated: 2025-09-24
---

# Data Model Overview

**en:** Conceptual view of assessment versions, item bank governance, response linkage, and exposure statistics.

**nb-NO:** Konseptuelt diagram over vurderingsversjoner, spørsmålsbank-styring, responskobling og eksponeringsstatistikk.

![ERD](../public/erd.svg)

<details>
<summary>Mermaid fallback</summary>

```mermaid
erDiagram
    ASSESSMENT_VERSIONS ||--o{ ASSESSMENT_ITEM_BANK : "contains"
    ASSESSMENT_ITEM_BANK ||--|| ASSESSMENT_ITEM_STATS : "tracks"
    ASSESSMENTS ||--o{ ASSESSMENT_RESPONSE_ITEMS : "records"
    ASSESSMENT_ITEM_BANK ||--o{ ASSESSMENT_RESPONSE_ITEMS : "delivers"
```

</details>
