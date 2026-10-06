## API Discovery Results

Query: Cost center master data + actual spend, count + top-5 ranking.

| Name | Type | ORD ID | Files |
|------|------|--------|-------|
| Cost Center | OData | sap.s4:apiResource:CE_COSTCENTER_0001:v1 | EDMX, OpenAPI JSON |
| Cost Center Hierarchy | OData | sap.s4:apiResource:CE_COSTCENTERHIERARCHY_0001:v1 | EDMX, OpenAPI JSON |
| Cost Center - Read (A2X) | OData | sap.s4:apiResource:API_COSTCENTER_SRV:v1 | EDMX, OpenAPI JSON |
| Commitment and Actual Items (A2X) | OData | sap.s4:apiResource:API_PUBSECCMTMTACTLITEM:v1 | EDMX, OpenAPI JSON |
| Controlling Area - Read | OData | sap.s4:apiResource:API_CONTROLLINGAREA_SRV:v1 | EDMX, OpenAPI JSON |
| Journal Entry (Cost Controlling) | OData | sap.s4:apiResource:API_COSTREVNREASSIGNMENT:v1 | EDMX, OpenAPI JSON |

Selected (user decision: master data only):
- CE_COSTCENTER_0001:v1 — EDMX downloaded to api-specs/CE_COSTCENTER_0001.edmx

Not included: actual-spend API (API_PUBSECCMTMTACTLITEM). User chose master-data-only scope.
Consequence: agent answers total count reliably. Top-5-by-actual-spend only possible if
CE_COSTCENTER_0001 exposes a spend field; master data API typically does not. If ranking
is required, re-run discovery and add API_PUBSECCMTMTACTLITEM:v1.

