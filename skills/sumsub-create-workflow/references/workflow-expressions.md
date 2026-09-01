# Workflow expression reference

Authoritative inventory of every legal `exp` path and field type used in workflow edge conditions, generated from Sumsub's `WorkflowExpressionContext` schema. **This file supersedes the illustrative tables in `workflow-schema.md` and `SKILL.md` when they disagree.** Open it whenever a workflow needs an `exp` path you can't quote from memory, or to verify a path before POSTing.

**Structure.**
- `## Types` — one table per type. Start here to explore a namespace (`applicant`, `poi`, `checks`, …).
- `## Index` — flat alphabetical list of every legal dotted path as markdown links into the Types tables.

**Efficient access — don't read end-to-end; this is a lookup database.**

- **Validate a path:** `grep '<leafFieldName>' workflow-expressions.md`. The leaf field name (the last component of the path) appears verbatim in both the Types row and the Index entry. Searching for a full dotted path like `applicant.review.attemptCnt` returns no matches — the Index renders each segment as a markdown link (`` [\`applicant\`](#...).[\`review\`](#...) ``) so the dotted form is not a contiguous substring.
- **Explore a namespace:** jump to the `### <TypeName>` section directly. Anchors are stable (`#ApplicantExpressionData`, `#PoiExpressionData`, `#BackgroundChecksExpressionData`, …).
- **Disambiguate same-named leaves:** the same leaf appears under multiple parents (e.g. `firstName` lives on `applicant.fixedInfo`, on `applicant.info`, and on each document's `crossCheckNameData`). The Index entry shows the full chain — pick the one matching your intent.

**Out of scope here.** This file lists *paths and field types* only. It does not enumerate operators (`eq`, `in`, `gt`, `notEmpty`, …) — see the operator list in `workflow-schema.md` (and the *Edge conditions* section of `SKILL.md`) for those. Some fields are typed as `Enum`; their value lists appear inline in the relevant table.

## Types

### <a name="WorkflowExpressionContext"></a>`Root variables`

| Field | Type | Description |
| --- | --- | --- |
| <a name="WorkflowExpressionContext.applicant"></a>`applicant` | [`Object`](#ApplicantExpressionData) | Applicant information |
| <a name="WorkflowExpressionContext.poi"></a>`poi` | [`Object`](#PoiExpressionData) | Proof of Identity Document |
| <a name="WorkflowExpressionContext.poi2"></a>`poi2` | [`Object`](#PoiExpressionData) | 2-nd Proof of Identity Document |
| <a name="WorkflowExpressionContext.poi3"></a>`poi3` | [`Object`](#PoiExpressionData) | 3-rd Proof of Identity Document |
| <a name="WorkflowExpressionContext.poi4"></a>`poi4` | [`Object`](#PoiExpressionData) | 4-th Proof of Identity Document |
| <a name="WorkflowExpressionContext.poa"></a>`poa` | [`Object`](#PoaExpressionData) | Proof of Address Document |
| <a name="WorkflowExpressionContext.poa2"></a>`poa2` | [`Object`](#PoaExpressionData) | 2-nd Proof of Address Document |
| <a name="WorkflowExpressionContext.device"></a>`device` | [`Object`](#DeviceExpressionData) | Applicant device information |
| <a name="WorkflowExpressionContext.deviceStats"></a>`deviceStats` | [`Object`](#DeviceStatsExpressionData) | Applicant device statistics |
| <a name="WorkflowExpressionContext.questionnaires"></a>`questionnaires` | Map of `Object`-s | Questionnaire item values nested by questionnaire, then section, then item id. <p> E.g. `questionnaire["myQuestionnaireId"]["mySectionId"]["myItemId"]` |
| <a name="WorkflowExpressionContext.clientLists"></a>`clientLists` | Map of `Object`-s | Client Lists by name |
| <a name="WorkflowExpressionContext.checks"></a>`checks` | [`Object`](#BackgroundChecksExpressionData) | Background checks information |
| <a name="WorkflowExpressionContext.action"></a>`action` | [`Object`](#ApplicantActionExpressionData) | Applicant action information |
| <a name="WorkflowExpressionContext.random"></a>`random` | `Double` | Random number between 0.0 and 1.0 |

### <a name="ApplicantExpressionData"></a>`applicant`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantExpressionData.id"></a>`id` | `String` | Applicant ID |
| <a name="ApplicantExpressionData.externalUserId"></a>`externalUserId` | `String` | Applicant external ID |
| <a name="ApplicantExpressionData.createdAt"></a>`createdAt` | [`Date`](#DateExpressionData) | Applicant creation date |
| <a name="ApplicantExpressionData.registrationDate"></a>`registrationDate` | [`Date`](#DateExpressionData) | Client started the relationship with the applicant |
| <a name="ApplicantExpressionData.fullName"></a>`fullName` | `String` | Full name of the applicant |
| <a name="ApplicantExpressionData.country"></a>`country` | `String` | Applicant country (ISO 3166-1 alpha-3) |
| <a name="ApplicantExpressionData.countryOfBirth"></a>`countryOfBirth` | `String` | Applicant country of birth (ISO 3166-1 alpha-3) |
| <a name="ApplicantExpressionData.info"></a>`info` | [`Object`](#ApplicantInfoExpressionData) | Applicant information extracted from documents |
| <a name="ApplicantExpressionData.fixedInfo"></a>`fixedInfo` | [`Object`](#ApplicantInfoExpressionData) | Basic applicant information as provided to our SDK/API/Dashboard |
| <a name="ApplicantExpressionData.review"></a>`review` | [`Object`](#InspectionReviewExpressionData) | Applicant review |
| <a name="ApplicantExpressionData.sourceKey"></a>`sourceKey` | `String` | Source key of the applicant |
| <a name="ApplicantExpressionData.derivatives"></a>`derivatives` | [`Object`](#ApplicantDerivatives) | Various information derived from the applicant |
| <a name="ApplicantExpressionData.metadata"></a>`metadata` | Map of `String`-s | Applicant metadata |
| <a name="ApplicantExpressionData.riskLabels"></a>`riskLabels` | [`Object`](#ApplicantRiskLabels) | Applicant risk labels |
| <a name="ApplicantExpressionData.tags"></a>`tags` | List of `String`-s | Applicant tags |
| <a name="ApplicantExpressionData.assessment"></a>`assessment` | [`Object`](#ApplicantAssessmentExpressionData) | Applicant assessment |
| <a name="ApplicantExpressionData.email"></a>`email` | `String` | Applicant email |
| <a name="ApplicantExpressionData.phone"></a>`phone` | [`Object`](#PhoneExpressionData) | Applicant phone |
| <a name="ApplicantExpressionData.emailDomain"></a>`emailDomain` | `String` | Applicant email domain name |
| <a name="ApplicantExpressionData.type"></a>`type` | [`Enum`](#ApplicantType) | Applicant entity type: `individual` or `company` |
| <a name="ApplicantExpressionData.lang"></a>`lang` | `String` |  |
| <a name="ApplicantExpressionData.allMemberRoles"></a>`allMemberRoles` | List of `String`-s | Roles of the applicant |

### <a name="PoiExpressionData"></a>`poi, poi2, poi3, poi4`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PoiExpressionData.crossCheckNameData"></a>`crossCheckNameData` | [`Object`](#CrossCheckNameData) | Data from the document that we use for cross-validation |
| <a name="PoiExpressionData.crossCheckParentName1"></a>`crossCheckParentName1` | [`Object`](#CrossCheckFullNameData) | Parent name Data from the document that we use for cross-validation |
| <a name="PoiExpressionData.crossCheckParentName2"></a>`crossCheckParentName2` | [`Object`](#CrossCheckFullNameData) | Parent name Data from the document that we use for cross-validation |
| <a name="PoiExpressionData.country"></a>`country` | `String` | ID Document country (ISO 3166-1 alpha-3) |
| <a name="PoiExpressionData.idDocType"></a>`idDocType` | `Object` | ID Document type |
| <a name="PoiExpressionData.number"></a>`number` | `String` | ID Document number |
| <a name="PoiExpressionData.additionalNumber"></a>`additionalNumber` | `String` | ID Document additional number |
| <a name="PoiExpressionData.dob"></a>`dob` | [`Date`](#DateExpressionData) | Date of birth |
| <a name="PoiExpressionData.nationality"></a>`nationality` | `String` | Nationality (ISO 3166-1 alpha-3) |
| <a name="PoiExpressionData.placeOfBirth"></a>`placeOfBirth` | `String` | Place of birth |
| <a name="PoiExpressionData.issuedDate"></a>`issuedDate` | [`Date`](#DateExpressionData) | ID Document issue date |
| <a name="PoiExpressionData.issueAuthority"></a>`issueAuthority` | `String` | Authority that issued the ID Document. |
| <a name="PoiExpressionData.issueAuthorityCode"></a>`issueAuthorityCode` | `String` | A unique code of the authority that issued the ID Document. |
| <a name="PoiExpressionData.validUntil"></a>`validUntil` | [`Date`](#DateExpressionData) | ID Document validity date |
| <a name="PoiExpressionData.validityPeriod"></a>`validityPeriod` | [`Object`](#TimespanExpressionData) | ID Document's validity period |
| <a name="PoiExpressionData.firstIssuedDate"></a>`firstIssuedDate` | [`Date`](#DateExpressionData) | ID Document first issue date |
| <a name="PoiExpressionData.metadata"></a>`metadata` | Map of `String`-s | POI metadata. |
| <a name="PoiExpressionData.address"></a>`address` | [`Object`](#AddressExpressionData) | ID Document address |
| <a name="PoiExpressionData.category"></a>`category` | `String` | ID Document category, e.g., category of a driver's license |
| <a name="PoiExpressionData.nfc"></a>`nfc` | [`Object`](#NfcInfoExpressionData) | ID Document NFC information |
| <a name="PoiExpressionData.fullMrz"></a>`fullMrz` | `String` | Machine-Readable Zone lines separated by End of Line (`\n`) symbol |
| <a name="PoiExpressionData.gender"></a>`gender` | `String` | Gender (M or F) |
| <a name="PoiExpressionData.violations"></a>`violations` | [`Object`](#DocViolationsExpressionData) | MRZ / Barcode / DFR violations |
| <a name="PoiExpressionData.ocrDocTypes"></a>`ocrDocTypes` | List of `String`-s | Fine-grained Doc types from OCR |
| <a name="PoiExpressionData.dlCategoryBValidUntil"></a>`dlCategoryBValidUntil` | [`Date`](#DateExpressionData) | Expiry date of category B |

### <a name="PoaExpressionData"></a>`poa, poa2`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PoaExpressionData.crossCheckNameData"></a>`crossCheckNameData` | [`Object`](#CrossCheckNameData) | Data from the document that we use for cross-validation |
| <a name="PoaExpressionData.country"></a>`country` | `String` | ID Document country (ISO 3166-1 alpha-3) |
| <a name="PoaExpressionData.idDocType"></a>`idDocType` | `Object` | ID Document type |
| <a name="PoaExpressionData.number"></a>`number` | `String` | ID Document number |
| <a name="PoaExpressionData.metadata"></a>`metadata` | Map of `String`-s | PoA metadata. |
| <a name="PoaExpressionData.address"></a>`address` | [`Object`](#AddressExpressionData) | ID Document address |
| <a name="PoaExpressionData.issuedDate"></a>`issuedDate` | [`Date`](#DateExpressionData) | ID Document issue date |
| <a name="PoaExpressionData.detectedLanguages"></a>`detectedLanguages` | List of `String`-s | List of 2-letter codes (ISO 639-1) of detected languages. |
| <a name="PoaExpressionData.image"></a>`image` | [`Object`](#ImageExpressionData) | Image's technical details |
| <a name="PoaExpressionData.dob"></a>`dob` | [`Date`](#DateExpressionData) | Date of birth |
| <a name="PoaExpressionData.gender"></a>`gender` | `String` | Gender (M or F) |
| <a name="PoaExpressionData.violations"></a>`violations` | [`Object`](#DocViolationsExpressionData) | MRZ / Barcode / DFR violations |
| <a name="PoaExpressionData.ocrDocTypes"></a>`ocrDocTypes` | List of `String`-s | Fine-grained Doc types from OCR |

### <a name="DeviceExpressionData"></a>`device`

| Field | Type | Description |
| --- | --- | --- |
| <a name="DeviceExpressionData.ipCountry"></a>`ipCountry` | `String` | IP Address Country (ISO 3166-1 alpha-3) |
| <a name="DeviceExpressionData.ipStateCode"></a>`ipStateCode` | `String` |  |
| <a name="DeviceExpressionData.info"></a>`info` | [`Object`](#DeviceInfoExpressionData) |  |

### <a name="DeviceStatsExpressionData"></a>`deviceStats`

| Field | Type | Description |
| --- | --- | --- |
| <a name="DeviceStatsExpressionData.minutes5"></a>`minutes5` | [`Object`](#DevicePeriodStatsExpressionData) | Running 5-minute stats |
| <a name="DeviceStatsExpressionData.hours1"></a>`hours1` | [`Object`](#DevicePeriodStatsExpressionData) | Running 1-hour stats |
| <a name="DeviceStatsExpressionData.days1"></a>`days1` | [`Object`](#DevicePeriodStatsExpressionData) | Running 1-day stats |
| <a name="DeviceStatsExpressionData.days7"></a>`days7` | [`Object`](#DevicePeriodStatsExpressionData) | Running 7-day stats |

### <a name="BackgroundChecksExpressionData"></a>`checks`

| Field | Type | Description |
| --- | --- | --- |
| <a name="BackgroundChecksExpressionData.all"></a>`all` | [`Object`](#AllBackgroundChecksExpressionData) | Aggregated information about all checks by type |
| <a name="BackgroundChecksExpressionData.poa"></a>`poa` | [`Object`](#PoaCheckExpressionData) | POA information (UTILITY_BILL) |
| <a name="BackgroundChecksExpressionData.poa2"></a>`poa2` | [`Object`](#PoaCheckExpressionData) | POA2 information (UTILITY_BILL2) |
| <a name="BackgroundChecksExpressionData.ekyc"></a>`ekyc` | [`Object`](#EkycCheckExpressionData) | E_KYC information |
| <a name="BackgroundChecksExpressionData.company"></a>`company` | [`Object`](#CompanyCheckExpressionData) | Company information |
| <a name="BackgroundChecksExpressionData.companyTax"></a>`companyTax` | [`Object`](#CompanyTaxCheckExpressionData) | Company tax information |
| <a name="BackgroundChecksExpressionData.companyStructure"></a>`companyStructure` | [`Object`](#CompanyStructureCheckExpressionData) | Company structure information |
| <a name="BackgroundChecksExpressionData.customDataSources"></a>`customDataSources` | Map of [`Object`](#CustomDataSourceExpressionData)-s | Custom data sources |
| <a name="BackgroundChecksExpressionData.personWatchlist"></a>`personWatchlist` | [`Object`](#PersonWatchlistCheckExpressionData) | Watchlist matching the person |
| <a name="BackgroundChecksExpressionData.companyWatchlist"></a>`companyWatchlist` | [`Object`](#CompanyWatchlistCheckExpressionData) | Watchlist matching the company |
| <a name="BackgroundChecksExpressionData.email"></a>`email` | [`Object`](#EmailConfirmationCheckExpressionData) | Email confirmation |
| <a name="BackgroundChecksExpressionData.phone"></a>`phone` | [`Object`](#PhoneConfirmationCheckExpressionData) | Phone confirmation |
| <a name="BackgroundChecksExpressionData.ip"></a>`ip` | [`Object`](#IpCheckExpressionData) | IP information |
| <a name="BackgroundChecksExpressionData.paymentSource"></a>`paymentSource` | [`Object`](#PaymentSourceCheckInfoExpressionData) | Payment source check info |
| <a name="BackgroundChecksExpressionData.nfcCheck"></a>`nfcCheck` | [`Object`](#NfcCheckExpressionData) | NFC source check info |

### <a name="ApplicantActionExpressionData"></a>`action`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantActionExpressionData.id"></a>`id` | `String` | Action ID |
| <a name="ApplicantActionExpressionData.externalActionId"></a>`externalActionId` | `String` | Action external ID |
| <a name="ApplicantActionExpressionData.createdAt"></a>`createdAt` | [`Date`](#DateExpressionData) | Action creation date |
| <a name="ApplicantActionExpressionData.review"></a>`review` | [`Object`](#InspectionReviewExpressionData) | Action review |
| <a name="ApplicantActionExpressionData.paymentSource"></a>`paymentSource` | [`Object`](#PaymentSourceExpressionData) | Payment Source info |
| <a name="ApplicantActionExpressionData.metadata"></a>`metadata` | Map of `String`-s | Action metadata |
| <a name="ApplicantActionExpressionData.actionFixedInfo"></a>`actionFixedInfo` | [`Object`](#ApplicantInfoExpressionData) | Basic applicant information as provided to our SDK/API/Dashboard |
| <a name="ApplicantActionExpressionData.questionnaires"></a>`questionnaires` | Map of `Object`-s | Questionnaire item values nested by questionnaire, then section, then item id. <p> E.g. `questionnaire["myQuestionnaireId"]["mySectionId"]["myItemId"]` |
| <a name="ApplicantActionExpressionData.checks"></a>`checks` | [`Object`](#BackgroundChecksActionExpressionData) |  |

### <a name="DateExpressionData"></a>`date`

| Field | Type | Description |
| --- | --- | --- |
| <a name="DateExpressionData.timestamp"></a>`timestamp` | `long` | Unix timestamp in milliseconds |
| <a name="DateExpressionData.yyyymmdd"></a>`yyyymmdd` | `int` | Numeric day in YYYYMMDD format, e.g. 20230123 |
| <a name="DateExpressionData.year"></a>`year` | `int` | Year |
| <a name="DateExpressionData.month"></a>`month` | `int` | Month of year (starts from 1) |
| <a name="DateExpressionData.dayOfMonth"></a>`dayOfMonth` | `int` | Day of month (start from 1) |
| <a name="DateExpressionData.ageInYears"></a>`ageInYears` | `int` | Time dela in years between this date and now |
| <a name="DateExpressionData.ageInDays"></a>`ageInDays` | `int` | Time delta in days between this date and now |

### <a name="ApplicantInfoExpressionData"></a>`applicant.info`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantInfoExpressionData.crossCheckNameData"></a>`crossCheckNameData` | [`Object`](#CrossCheckNameData) | Data that we use for cross-validation |
| <a name="ApplicantInfoExpressionData.crossCheckParentName1"></a>`crossCheckParentName1` | [`Object`](#CrossCheckFullNameData) | Parent name data that we use for cross-validation |
| <a name="ApplicantInfoExpressionData.crossCheckParentName2"></a>`crossCheckParentName2` | [`Object`](#CrossCheckFullNameData) | Parent name data that we use for cross-validation |
| <a name="ApplicantInfoExpressionData.country"></a>`country` | `String` | Applicant country (ISO 3166-1 alpha-3) |
| <a name="ApplicantInfoExpressionData.countryOfBirth"></a>`countryOfBirth` | `String` | Applicant country of birth (ISO 3166-1 alpha-3) |
| <a name="ApplicantInfoExpressionData.firstName"></a>`firstName` | `String` | First name |
| <a name="ApplicantInfoExpressionData.firstNameEn"></a>`firstNameEn` | `String` | Transliterated first name |
| <a name="ApplicantInfoExpressionData.middleName"></a>`middleName` | `String` | Middle name |
| <a name="ApplicantInfoExpressionData.middleNameEn"></a>`middleNameEn` | `String` | Transliterated middle name |
| <a name="ApplicantInfoExpressionData.lastName"></a>`lastName` | `String` | Last name |
| <a name="ApplicantInfoExpressionData.lastNameEn"></a>`lastNameEn` | `String` | Transliterated last name |
| <a name="ApplicantInfoExpressionData.gender"></a>`gender` | `String` | Gender (M or F) |
| <a name="ApplicantInfoExpressionData.nationality"></a>`nationality` | `String` | Nationality (ISO 3166-1 alpha-3) |
| <a name="ApplicantInfoExpressionData.taxResidenceCountry"></a>`taxResidenceCountry` | `String` | Tax Residence Country (ISO 3166-1 alpha-3) |
| <a name="ApplicantInfoExpressionData.residenceCountry"></a>`residenceCountry` | `String` | Residence Country (ISO 3166-1 alpha-3) |
| <a name="ApplicantInfoExpressionData.age"></a>`age` | `Integer` | Applicant age |
| <a name="ApplicantInfoExpressionData.dob"></a>`dob` | [`Date`](#DateExpressionData) | Date of birth |
| <a name="ApplicantInfoExpressionData.address"></a>`address` | [`Object`](#AddressExpressionData) | Applicant address |
| <a name="ApplicantInfoExpressionData.addresses"></a>`addresses` | [`Object`](#ApplicantInfoAddressesExpressionData) |  |
| <a name="ApplicantInfoExpressionData.companyInfo"></a>`companyInfo` | [`Object`](#CompanyInfoExpressionData) | Company information (KYB) |
| <a name="ApplicantInfoExpressionData.tinCountries"></a>`tinCountries` | List of `String`-s | Countries from TINs (ISO 3166-1 alpha-3) |
| <a name="ApplicantInfoExpressionData.tin"></a>`tin` | `String` |  |
| <a name="ApplicantInfoExpressionData.phone"></a>`phone` | [`Object`](#PhoneExpressionData) |  |

### <a name="InspectionReviewExpressionData"></a>`applicant.review, action.review`

| Field | Type | Description |
| --- | --- | --- |
| <a name="InspectionReviewExpressionData.levelName"></a>`levelName` | `String` | Applicant level |
| <a name="InspectionReviewExpressionData.decision"></a>`decision` | [`Enum`](#ReviewDecision) | Review decision |
| <a name="InspectionReviewExpressionData.reviewAnswer"></a>`reviewAnswer` | [`Enum`](#ImageTestAnswer) | Review answer |
| <a name="InspectionReviewExpressionData.attemptCnt"></a>`attemptCnt` | `Integer` | Number of attempts |
| <a name="InspectionReviewExpressionData.rejectLabels"></a>`rejectLabels` | List of [`Enum`](#ReviewResult.ReviewLabel)-s | List of rejection labels |
| <a name="InspectionReviewExpressionData.buttonIds"></a>`buttonIds` | List of `String`-s | List of button ids |

### <a name="ApplicantDerivatives"></a>`applicant.derivatives`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantDerivatives.estimatedAge"></a>`estimatedAge` | `Integer` | Applicant estimated age. |

### <a name="ApplicantRiskLabels"></a>`riskLabels`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantRiskLabels.email"></a>`email` | List of [`Enum`](#EmailRiskLabel)-s | Email risk labels |
| <a name="ApplicantRiskLabels.phone"></a>`phone` | List of [`Enum`](#PhoneRiskLabel)-s | Phone risk labels |
| <a name="ApplicantRiskLabels.device"></a>`device` | List of [`Enum`](#DeviceRiskLabel)-s | Device risk labels |
| <a name="ApplicantRiskLabels.deviceCheck"></a>`deviceCheck` | List of [`Enum`](#AntifraudDeviceCheckRiskLabel)-s | Device check risk labels |
| <a name="ApplicantRiskLabels.crossCheck"></a>`crossCheck` | List of [`Enum`](#CrossCheckRiskLabel)-s | Cross-check risk labels |
| <a name="ApplicantRiskLabels.selfie"></a>`selfie` | List of [`Enum`](#SelfieRiskLabel)-s | Selfie risk labels |
| <a name="ApplicantRiskLabels.aml"></a>`aml` | List of [`Enum`](#AmlRiskLabel)-s | AML risk labels |
| <a name="ApplicantRiskLabels.person"></a>`person` | List of [`Enum`](#PersonRiskLabel)-s | Person risk labels |
| <a name="ApplicantRiskLabels.company"></a>`company` | List of [`Enum`](#CompanyRiskLabel)-s | Company risk labels |

### <a name="ApplicantAssessmentExpressionData"></a>`applicant.assessment`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantAssessmentExpressionData.totalScore"></a>`totalScore` | `Float` |  |
| <a name="ApplicantAssessmentExpressionData.scores"></a>`scores` | Map of [`Object`](#ApplicantAssessmentResultExpressionData)-s |  |

### <a name="PhoneExpressionData"></a>`phone`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PhoneExpressionData.number"></a>`number` | `String` |  |
| <a name="PhoneExpressionData.country"></a>`country` | `String` |  |

### <a name="ApplicantType"></a>`applicant.type`

| Value | Description |
| --- | --- |
| `individual` | Individual applicant. |
| `company` | Company applicant. |

### <a name="CrossCheckNameData"></a>`crossCheckNameData`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CrossCheckNameData.country"></a>`country` | `String` |  |
| <a name="CrossCheckNameData.firstName"></a>`firstName` | `String` |  |
| <a name="CrossCheckNameData.middleName"></a>`middleName` | `String` |  |
| <a name="CrossCheckNameData.lastName"></a>`lastName` | `String` |  |
| <a name="CrossCheckNameData.aliasName"></a>`aliasName` | `String` |  |

### <a name="CrossCheckFullNameData"></a>`crossCheckParentName1, crossCheckParentName2`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CrossCheckFullNameData.country"></a>`country` | `String` |  |
| <a name="CrossCheckFullNameData.fullName"></a>`fullName` | `String` |  |

### <a name="TimespanExpressionData"></a>`validityPeriod`

| Field | Type | Description |
| --- | --- | --- |
| <a name="TimespanExpressionData.millis"></a>`millis` | `long` | Milliseconds |
| <a name="TimespanExpressionData.days"></a>`days` | `long` | Days |
| <a name="TimespanExpressionData.hours"></a>`hours` | `long` | Hours |
| <a name="TimespanExpressionData.minutes"></a>`minutes` | `long` | Minutes |
| <a name="TimespanExpressionData.seconds"></a>`seconds` | `long` | Seconds |

### <a name="AddressExpressionData"></a>`address`

| Field | Type | Description |
| --- | --- | --- |
| <a name="AddressExpressionData.country"></a>`country` | `String` | Country code (ISO 3166-1 alpha-3). |
| <a name="AddressExpressionData.formattedAddress"></a>`formattedAddress` | `String` |  |
| <a name="AddressExpressionData.state"></a>`state` | `String` | State name or region if applicable. |
| <a name="AddressExpressionData.stateCode"></a>`stateCode` | `String` | ISO 3166-2 state code |
| <a name="AddressExpressionData.town"></a>`town` | `String` | Town if applicable. |
| <a name="AddressExpressionData.street"></a>`street` | `String` | Street if applicable. |
| <a name="AddressExpressionData.subStreet"></a>`subStreet` | `String` | Street (line 2) if applicable. |
| <a name="AddressExpressionData.postCode"></a>`postCode` | `String` | Post code if applicable. |
| <a name="AddressExpressionData.buildingName"></a>`buildingName` | `String` |  |
| <a name="AddressExpressionData.buildingNumber"></a>`buildingNumber` | `String` |  |
| <a name="AddressExpressionData.flatNumber"></a>`flatNumber` | `String` |  |

### <a name="NfcInfoExpressionData"></a>`nfc`

Information read from NFC Chip

| Field | Type | Description |
| --- | --- | --- |
| <a name="NfcInfoExpressionData.fullMrz"></a>`fullMrz` | `String` | Full MRZ |

### <a name="DocViolationsExpressionData"></a>`violations`

| Field | Type | Description |
| --- | --- | --- |
| <a name="DocViolationsExpressionData.mrz"></a>`mrz` | List of [`Enum`](#BackgroundCheckViolation)-s |  |
| <a name="DocViolationsExpressionData.dfr"></a>`dfr` | List of [`Enum`](#BackgroundCheckViolation)-s |  |
| <a name="DocViolationsExpressionData.barcode"></a>`barcode` | List of [`Enum`](#BackgroundCheckViolation)-s |  |

### <a name="ImageExpressionData"></a>`poa.image, poa2.image`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ImageExpressionData.softwareTag"></a>`softwareTag` | `String` | Software |
| <a name="ImageExpressionData.mimeType"></a>`mimeType` | [`Enum`](#MediaTypeId) |  |

### <a name="DeviceInfoExpressionData"></a>`device.info`

| Field | Type | Description |
| --- | --- | --- |
| <a name="DeviceInfoExpressionData.make"></a>`make` | `String` |  |
| <a name="DeviceInfoExpressionData.model"></a>`model` | `String` |  |
| <a name="DeviceInfoExpressionData.type"></a>`type` | `String` |  |
| <a name="DeviceInfoExpressionData.platform"></a>`platform` | `String` |  |
| <a name="DeviceInfoExpressionData.platformVersion"></a>`platformVersion` | `String` |  |
| <a name="DeviceInfoExpressionData.browser"></a>`browser` | `String` |  |
| <a name="DeviceInfoExpressionData.browserFullVersion"></a>`browserFullVersion` | `String` |  |

### <a name="DevicePeriodStatsExpressionData"></a>`deviceStats.minutes5`

| Field | Type | Description |
| --- | --- | --- |
| <a name="DevicePeriodStatsExpressionData.riskLevel"></a>`riskLevel` | [`Enum`](#ImageTestAnswer) |  |
| <a name="DevicePeriodStatsExpressionData.deviceCount"></a>`deviceCount` | `Integer` | Number of devices of an applicant within a period |
| <a name="DevicePeriodStatsExpressionData.sameDeviceApplicantCount"></a>`sameDeviceApplicantCount` | `Integer` | Number of applicants that share any device with this applicant within a period (0 if noone else shares any device) |
| <a name="DevicePeriodStatsExpressionData.riskLabels"></a>`riskLabels` | List of `String`-s | All risk labels associated with the applicant's devices within a period |
| <a name="DevicePeriodStatsExpressionData.deviceIds"></a>`deviceIds` | List of `String`-s | Applicant device ids |

### <a name="AllBackgroundChecksExpressionData"></a>`checks.all`

| Field | Type | Description |
| --- | --- | --- |
| <a name="AllBackgroundChecksExpressionData.ip"></a>`ip` | [`Object`](#AllIpChecksExpressionData) | Aggregated IP check information |

### <a name="PoaCheckExpressionData"></a>`checks.poa, checks.poa2`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PoaCheckExpressionData.companyType"></a>`companyType` | [`Enum`](#PoaCompanyContactType) | POA company type |
| <a name="PoaCheckExpressionData.subType"></a>`subType` | [`Enum`](#PoaSubType) | POA sub type if applicable |
| <a name="PoaCheckExpressionData.unconventionalProvider"></a>`unconventionalProvider` | `Boolean` | Indicates whether POA was obtained via an unconventional provider, e.g. a neo-bank if companyType equals "bank". |

### <a name="EkycCheckExpressionData"></a>`checks.ekyc`

| Field | Type | Description |
| --- | --- | --- |
| <a name="EkycCheckExpressionData.extractedData"></a>`extractedData` | [`Object`](#BgCheckExtractedExpressionData) | Extracted data from an external source |
| <a name="EkycCheckExpressionData.violations"></a>`violations` | List of [`Enum`](#BackgroundCheckViolation)-s | List of NonDoc step violations |

### <a name="CompanyCheckExpressionData"></a>`checks.company`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyCheckExpressionData.answer"></a>`answer` | [`Enum`](#ImageTestAnswer) | Company check answer |
| <a name="CompanyCheckExpressionData.info"></a>`info` | [`Object`](#CompanyCheckInfoExpressionData) | Additional company check data. |

### <a name="CompanyTaxCheckExpressionData"></a>`checks.companyTax`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyTaxCheckExpressionData.answer"></a>`answer` | [`Enum`](#ImageTestAnswer) |  |

### <a name="CompanyStructureCheckExpressionData"></a>`checks.companyStructure`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyStructureCheckExpressionData.answer"></a>`answer` | [`Enum`](#ImageTestAnswer) |  |

### <a name="CustomDataSourceExpressionData"></a>`Elements of checks.customDataSources`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CustomDataSourceExpressionData.success"></a>`success` | `Boolean` |  |
| <a name="CustomDataSourceExpressionData.output"></a>`output` | Map of `Object`-s |  |

### <a name="PersonWatchlistCheckExpressionData"></a>`checks.personWatchlist`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PersonWatchlistCheckExpressionData.matchStatuses"></a>`matchStatuses` | List of `String`-s | Watchlist match statuses for the person. Either one of "unknown", "no_match", "potential_match", "false_positive", or "true_positive". |
| <a name="PersonWatchlistCheckExpressionData.ongoingMatchStatuses"></a>`ongoingMatchStatuses` | List of `String`-s | Statuses of matches received in the latest ongoing update. Either one of "unknown", "no_match", "potential_match", "false_positive", or "true_positive". |
| <a name="PersonWatchlistCheckExpressionData.ongoingUpdatedAt"></a>`ongoingUpdatedAt` | [`Date`](#DateExpressionData) | Date and time of the latest ongoing update of AML matches, if any. |
| <a name="PersonWatchlistCheckExpressionData.tags"></a>`tags` | List of `String`-s | Tags can be added by AML rule with purpose to check it in another rule. |

### <a name="CompanyWatchlistCheckExpressionData"></a>`checks.companyWatchlist`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyWatchlistCheckExpressionData.matchStatuses"></a>`matchStatuses` | List of `String`-s | Watchlist match statuses for the company. Either one of "unknown", "no_match", "potential_match", "false_positive", or "true_positive". |
| <a name="CompanyWatchlistCheckExpressionData.tags"></a>`tags` | List of `String`-s | Tags can be added by AML rule with purpose to check it in another rule. |

### <a name="EmailConfirmationCheckExpressionData"></a>`checks.email`

| Field | Type | Description |
| --- | --- | --- |
| <a name="EmailConfirmationCheckExpressionData.confirmedViaOtp"></a>`confirmedViaOtp` | [`Enum`](#ImageTestAnswer) | Email OTP confirmation answer |
| <a name="EmailConfirmationCheckExpressionData.nonDisposable"></a>`nonDisposable` | [`Enum`](#ImageTestAnswer) | Non-disposable email answer |
| <a name="EmailConfirmationCheckExpressionData.blacklisted"></a>`blacklisted` | [`Enum`](#ImageTestAnswer) | Blocklisted email answer |

### <a name="PhoneConfirmationCheckExpressionData"></a>`checks.phone`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PhoneConfirmationCheckExpressionData.confirmedViaOtp"></a>`confirmedViaOtp` | [`Enum`](#ImageTestAnswer) | Phone OTP confirmation answer |
| <a name="PhoneConfirmationCheckExpressionData.blacklisted"></a>`blacklisted` | [`Enum`](#ImageTestAnswer) | Blocklisted phone answer |

### <a name="IpCheckExpressionData"></a>`checks.ip`

| Field | Type | Description |
| --- | --- | --- |
| <a name="IpCheckExpressionData.country"></a>`country` | `String` | IP Address country |
| <a name="IpCheckExpressionData.vpn"></a>`vpn` | [`Enum`](#ImageTestAnswer) | IP Address VPN answer |
| <a name="IpCheckExpressionData.tor"></a>`tor` | [`Enum`](#ImageTestAnswer) | IP Address TOR answer |
| <a name="IpCheckExpressionData.proxy"></a>`proxy` | [`Enum`](#ImageTestAnswer) | IP Address PROXY answer |
| <a name="IpCheckExpressionData.riskLevel"></a>`riskLevel` | [`Enum`](#ImageTestAnswer) | IP Address Risk Level |

### <a name="PaymentSourceCheckInfoExpressionData"></a>`checks.paymentSource, action.checks.paymentSource`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PaymentSourceCheckInfoExpressionData.extractedInfo"></a>`extractedInfo` | [`Object`](#PaymentSourceInfoExpressionData) |  |
| <a name="PaymentSourceCheckInfoExpressionData.riskCheck"></a>`riskCheck` | [`Object`](#PaymentSourceRiskCheckExpressionData) |  |

### <a name="NfcCheckExpressionData"></a>`checks.nfcCheck`

| Field | Type | Description |
| --- | --- | --- |
| <a name="NfcCheckExpressionData.validation"></a>`validation` | [`Object`](#NfcValidationExpressionData) |  |
| <a name="NfcCheckExpressionData.extractedData"></a>`extractedData` | [`Object`](#NfcExtractedDataExpressionData) |  |

### <a name="PaymentSourceExpressionData"></a>`action.paymentSource`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PaymentSourceExpressionData.fixedInfo"></a>`fixedInfo` | [`Object`](#PaymentSourceInfoExpressionData) | Payment source info predefined from a client or from user |
| <a name="PaymentSourceExpressionData.info"></a>`info` | [`Object`](#PaymentSourceInfoExpressionData) | Payment source info recognised from the image |

### <a name="BackgroundChecksActionExpressionData"></a>`action.checks`

| Field | Type | Description |
| --- | --- | --- |
| <a name="BackgroundChecksActionExpressionData.crossValidation"></a>`crossValidation` | [`Object`](#CrossValidationCheckExpressionData) |  |
| <a name="BackgroundChecksActionExpressionData.paymentSource"></a>`paymentSource` | [`Object`](#PaymentSourceCheckInfoExpressionData) | Payment source check info |

### <a name="ApplicantInfoAddressesExpressionData"></a>`addresses`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantInfoAddressesExpressionData.manual"></a>`manual` | [`Object`](#AddressExpressionData) | User manually filled address Applicant address |
| <a name="ApplicantInfoAddressesExpressionData.autoComplete"></a>`autoComplete` | [`Object`](#AddressExpressionData) | User used autocomplete to fill Applicant address |
| <a name="ApplicantInfoAddressesExpressionData.gps"></a>`gps` | [`Object`](#AddressExpressionData) | User used gps location to provide the address |
| <a name="ApplicantInfoAddressesExpressionData.externalDb"></a>`externalDb` | [`Object`](#AddressExpressionData) | External database was used to provide the address |
| <a name="ApplicantInfoAddressesExpressionData.proofOfAddress"></a>`proofOfAddress` | [`Object`](#AddressExpressionData) | Proof of an address document was used to provide the address |
| <a name="ApplicantInfoAddressesExpressionData.proofOfIdentity"></a>`proofOfIdentity` | [`Object`](#AddressExpressionData) | Identity document was used to provide the address |

### <a name="CompanyInfoExpressionData"></a>`companyInfo`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyInfoExpressionData.country"></a>`country` | `String` | Company country (ISO 3166-1 alpha-3) |
| <a name="CompanyInfoExpressionData.type"></a>`type` | `String` |  |
| <a name="CompanyInfoExpressionData.legalForm"></a>`legalForm` | `String` |  |
| <a name="CompanyInfoExpressionData.companyName"></a>`companyName` | `String` |  |
| <a name="CompanyInfoExpressionData.registrationNumber"></a>`registrationNumber` | `String` |  |
| <a name="CompanyInfoExpressionData.leiCode"></a>`leiCode` | `String` |  |
| <a name="CompanyInfoExpressionData.address"></a>`address` | [`Object`](#AddressExpressionData) |  |
| <a name="CompanyInfoExpressionData.legalAddress"></a>`legalAddress` | `String` |  |
| <a name="CompanyInfoExpressionData.postalAddress"></a>`postalAddress` | `String` |  |
| <a name="CompanyInfoExpressionData.registrationLocation"></a>`registrationLocation` | `String` |  |
| <a name="CompanyInfoExpressionData.incorporatedOn"></a>`incorporatedOn` | `Date` |  |
| <a name="CompanyInfoExpressionData.incorporationDate"></a>`incorporationDate` | [`Date`](#DateExpressionData) | Company incorporation date. |
| <a name="CompanyInfoExpressionData.email"></a>`email` | `String` |  |
| <a name="CompanyInfoExpressionData.phone"></a>`phone` | `String` |  |
| <a name="CompanyInfoExpressionData.taxId"></a>`taxId` | `String` |  |
| <a name="CompanyInfoExpressionData.website"></a>`website` | `String` |  |
| <a name="CompanyInfoExpressionData.noUBOs"></a>`noUBOs` | `Boolean` |  |
| <a name="CompanyInfoExpressionData.noShareholders"></a>`noShareholders` | `Boolean` |  |
| <a name="CompanyInfoExpressionData.beneficiallyHeld"></a>`beneficiallyHeld` | `Boolean` |  |
| <a name="CompanyInfoExpressionData.skippedTypes"></a>`skippedTypes` | List of `String`-s |  |
| <a name="CompanyInfoExpressionData.ownershipStructureDepth"></a>`ownershipStructureDepth` | `Integer` |  |
| <a name="CompanyInfoExpressionData.beneficiaryStats"></a>`beneficiaryStats` | [`Object`](#BeneficiaryStatsExpressionData) |  |
| <a name="CompanyInfoExpressionData.upcomingDocumentExpiration"></a>`upcomingDocumentExpiration` | [`Object`](#UpcomingDocumentExpirationExpressionData) |  |

### <a name="ReviewDecision"></a>`applicant.review.decision, action.review.decision`

| Value | Description |
| --- | --- |
| `approved` | Review is approved. |
| `rejected` | Review is rejected. |
| `resubmission` | Resubmission requested. |

### <a name="ImageTestAnswer"></a>`riskLevel`

Review answer

| Value | Description |
| --- | --- |
| `IGNORED` | Check was skipped. |
| `GREEN` | Everything is fine. |
| `YELLOW` | Fine with some warnings / but most likely undefined (requires attention, review) |
| `RED` | Some violations found. |
| `ERROR` | Error occurred. |

### <a name="ReviewResult.ReviewLabel"></a>`Elements of applicant.review.rejectLabels, Elements of action.review.rejectLabels`

Review Rejection label

| Value | Description |
| --- | --- |
| `FORGERY` | Forgery attempt |
| `CRIMINAL` | The user is involved in illegal actions |
| `DOCUMENT_TEMPLATE` | Documents supplied are templates, downloaded from the internet |
| `LOW_QUALITY` | Documents have low-quality that doesn't allow definitive conclusions to be made |
| `SPAM` | An applicant has been created by mistake or is just a spam user (irrelevant images were supplied) |
| `NOT_DOCUMENT` | Documents supplied aren't relevant for the verification procedure |
| `SELFIE_MISMATCH` | A user photo (profile image) doesn't match a photo on the provided documents |
| `ID_INVALID` | A document that identifies a person (like a passport or an ID card) is not valid |
| `DOCUMENT_DEPRIVED` | The user has been deprived of the document |
| `FOREIGNER` | When a client doesn't accept applicants from a different country or e.g. without a residence permit |
| `DUPLICATE` | This applicant was already created for this client, and duplicates aren't allowed by the regulations |
| `BAD_AVATAR` | Avatar doesn't meet the client's requirements |
| `WRONG_USER_REGION` | When applicants from certain regions/countries aren't allowed to be registered |
| `WRONG_ADDRESS` | The address from the documents doesn't match the address that the user entered |
| `INCOMPLETE_DOCUMENT` | Some information is missing from the document, or it's partially visible |
| `BLACKLIST` | The User is blocklisted by us |
| `BLOCKLIST` | The User is blocklisted by the client |
| `OTHER` | Some unclassified reason |
| `UNSATISFACTORY_PHOTOS` | There were problems with the photos, like poor quality or masked information |
| `GRAPHIC_EDITOR` | The document has been edited by a graphical editor |
| `DOCUMENT_PAGE_MISSING` | Some pages of a document are missing (if applicable) |
| `DOCUMENT_DAMAGED` | Document is damaged |
| `DIGITAL_DOCUMENT` | Document is digital and cannot be accepted |
| `REGULATIONS_VIOLATIONS` | Regulations violations |
| `INCONSISTENT_PROFILE` | Data or documents of different persons were uploaded to one applicant |
| `PROBLEMATIC_APPLICANT_DATA` | Applicant data doesn't match the data in the documents |
| `GPS_AS_POA_SKIPPED` | When GpsAsPoa was skipped && no image uploaded |
| `ADDITIONAL_DOCUMENT_REQUIRED` | Additional documents required to pass the check For image review |
| `MORE_DOCUMENTS_REQUIRED` | Additional documents required to pass the check For applicant review |
| `AGE_REQUIREMENT_MISMATCH` | The Age requirement is not met (e.g. can't rent a car to a person below 25yo) |
| `REQUESTED_DATA_MISMATCH` | Provided info doesn't match with recognized from document data |
| `EXPERIENCE_REQUIREMENT_MISMATCH` | Not enough experience (e.g. driving experience is not enough) |
| `COMPROMISED_PERSONS` | The user doesn't correspond to Compromised Person Politics |
| `PEP` | The user belongs to the PEP category |
| `ADVERSE_MEDIA` | The user was found in the adverse media |
| `FRAUDULENT_PATTERNS` | Fraudulent behavior was detected |
| `STOLEN_DOCS` | If the user flagged verification as not them via SNS ID => their documents were suspected stolen |
| `SANCTIONS` | The user was found on sanction lists |
| `NOT_ALL_CHECKS_COMPLETED` | All checks weren't completed |
| `FRONT_SIDE_MISSING` | Front side of the document is missing |
| `BACK_SIDE_MISSING` | Back side of the document is missing |
| `SCREENSHOTS` | The user uploaded screenshots |
| `BLACK_AND_WHITE` | The user uploaded black and white photos of documents |
| `INCOMPATIBLE_LANGUAGE` | The user should upload translation of his document |
| `EXPIRATION_DATE` | The user uploaded an expired document |
| `UNFILLED_ID` | The user uploaded the document without signatures and stamps |
| `BAD_SELFIE` | The user uploaded a bad selfie |
| `BAD_VIDEO_SELFIE` | The user uploaded a bad video selfie |
| `BAD_FACE_MATCHING` | Face check between a document and selfie failed |
| `BAD_PROOF_OF_IDENTITY` | The user uploaded a bad ID document |
| `BAD_PROOF_OF_ADDRESS` | The user uploaded a bad proof of address |
| `BAD_PROOF_OF_PAYMENT` | The user uploaded a bad proof of payment |
| `SELFIE_WITH_PAPER` | The user should upload a special selfie (e.g. selfie with paper and date on it) |
| `FRAUDULENT_LIVENESS` | There was an attempt to bypass liveness check |
| `EXTERNAL_DECISION_REJECTION` | Always final client reject (applicant status via api) |
| `OK` | Custom reject label |
| `COMPANY_NOT_DEFINED_STRUCTURE` | Couldn't establish the entity's control structure |
| `COMPANY_NOT_DEFINED_BENEFICIARIES` | Couldn't identify and duly verify the entity's beneficial owners |
| `COMPANY_NOT_VALIDATED_BENEFICIAL_OWNERS` | Not all beneficial owners have passed the KYC verification procedure |
| `COMPANY_NOT_VALIDATED_BENEFICIARIES` | Beneficiaries are not validated |
| `COMPANY_NOT_VALIDATED_DIRECTORS` | Not all directors have passed the KYC verification procedure |
| `COMPANY_NOT_DEFINED_REPRESENTATIVES` | Representatives are not defined |
| `COMPANY_NOT_VALIDATED_REPRESENTATIVES` | Representatives are not validated |
| `UNSUITABLE_DOCUMENT` | Document either doesn't fit the required type or lacks obligatory elements, like seal, apostille, or notary certification |
| `OUTDATED_DOCUMENT_VERSION` | Based on the publicly available state company register not the most recent version was provided |
| `COMPANY_NOT_DEFINED_OWNERSHIP_STRUCTURE` | Company ownership structure has not specified or differs from the one declared by the corporate documents |
| `COMPANY_INACTIVE_ENTITY` | According to the publicly available state company registry, the entity is inactive / dissolved / deregistered |
| `COMPANY_INCORRECT_DATA` | Provided company attributes like Name, Registration or Tax Number don't match the provided documents or the state company registry |
| `COMPANY_PROBLEMATIC_STRUCTURE` | There are officials in the control and ownership structure who got rejected |
| `COMPANY_DATA_MISMATCH` | Company attributes like Name, Registration on the provided documents doesn't the match state company registry |
| `APPLICANT_INTERRUPTED_INTERVIEW` | On Video Ident call user refused to finish the interview |
| `DOCUMENT_MISSING` | On Video Ident call user refused to show or didn't have required documents |
| `UNSUITABLE_ENV` | On Video Ident call user is either not alone or nor visible |
| `CONNECTION_INTERRUPTED` | Video Ident call connection was interrupted |
| `UNSUPPORTED_LANGUAGE` | Video Ident user do not speak language common to operator |
| `THIRD_PARTY_INVOLVED` | Video Ident user trying to pass verification to pass account to a third party |
| `INCORRECT_SOCIAL_NUMBER` | Incorrect TIN/SSN was provided to perform the check |
| `CHECK_UNAVAILABLE` | External database service is not available at the moment |
| `DB_DATA_NOT_FOUND` | Data not found in external database |
| `DB_DATA_MISMATCH` | Input data/doc does not match data from external database |
| `DB_NO_DATA_SOURCE` | Input data is not supported by any enabled source |
| `ESIGN_FAILED` | E-Sign failed, most likely due personal info mismatch. Required to retry QES flow |
| `RESTRICTED_PERSON` | Person is found in a restricted list (ex. Prohibited from betting) |
| `NO_APPLICANT` | Applicant could not join the call |
| `NO_SUITABLE_DOCS` | Applicant couldn't provide a suitable document. |
| `NOT_ALONE` | Applicant was not alone. |
| `CONNECTION_ISSUES` | Applicant had unsuitable internet connection. |
| `CAMERA_OR_LIGHTING_ISSUES` | Applicant had unsuitable camera or lighting conditions. |
| `SOUND_ISSUES` | Applicant had audio input/output device settings issues. |
| `PHONE_VERIFICATION_ISSUES` | Applicant was not able to complete TAN step. |
| `OTHER_VI_ISSUES` | Applicant needs to call back later, wasn't prepared or able to continue now. |
| `REFUSED_TO_CONTINUE` | Applicant refused to continue verification call. |
| `VIDEO_FILTERS_OR_MASKS` | Video filters have been applied. |
| `SUPPORTED_LANGUAGE_IS_NOT_AVAILABLE` | Applicant couldn't proceed on selected language. |
| `ADDITIONAL_DATA_REQUIRED` | Additional data is required to complete VI verification. |
| `VI_ATTEMPTS_LIMIT_REACHED` | VI attempts limit reached. |
| `BEHAVIOR` | Applicant demonstrated inappropriate response to the procedure requirements and/or called being in a condition not suitable to complete verification successfully. |
| `PERSON_MISMATCH` | Video call initiated not by application data holder. |
| `THIRD_PARTY_GUIDANCE` | Applicant was misled/forced to create this account by a third party. |
| `SPONSORED_VERIFICATION` | Applicant suspected in paid account opening. |
| `INSUFFICIENT_DATA` | FraudNetworks label Insufficient data to make a determination. |
| `INCORRECT_PATTERNS` | FraudNetworks label Network patterns incorrectly identified. |

### <a name="EmailRiskLabel"></a>`Elements of applicant.riskLabels.email`

| Value | Description |
| --- | --- |
| `mediumRisk` | Medium-risk email address. |
| `highRisk` | High-risk email address. |
| `disposable` | Temporary email address which is provided by a disposable email service and usually expires in a few minutes. |
| `noWebRegistrations` | Email registration is not detected. |
| `noWebsiteExists` | Email domain does not exist. |
| `nonDeliverable` | Messages fail to be delivered to this email address. |
| `blocklisted` |  |
| `invalidEmail` | Email address is invalid |
| `gibberish` | Email address is gibberish. Like 1hasdhjelsf@gmail.com |
| `freshEmail` | Email's First Seen date is recent — fresh email with short digital footprint history. |

### <a name="PhoneRiskLabel"></a>`Elements of applicant.riskLabels.phone`

| Value | Description |
| --- | --- |
| `mediumRisk` | Medium-risk phone number. |
| `highRisk` | High-risk phone number. |
| `virtual` | Virtual phone that allows a user to make calls through the internet and is not associated with a physical location. |
| `noWebRegistrations` | Phone number registration is not detected. |
| `blocklisted` |  |
| `disposable` | Disposable phone. |
| `freshPhone` | Phone's First Seen date is recent — fresh phone number with short digital footprint history. |
| `phoneCountryVsApplicantCountryMismatch` | Country of phone number mismatches the applicant country |
| `phoneCountryVsIpCountryMismatch` | The phone number country does not match the IP address country |
| `phoneCountryVsAddressCountryMismatch` | The phone number country does not match the physical address country |
| `phoneCountryVsEmailDomainCountryMismatch` | The phone number country does not match the email domain country |
| `phoneCountryVsCompanyCountryMismatch` | The phone number country does not match the company country |

### <a name="DeviceRiskLabel"></a>`Elements of applicant.riskLabels.device`

| Value | Description |
| --- | --- |
| `vpnUsage` | VPN usage is detected. |
| `torUsage` | TOR usage is detected. |
| `highRiskIp` | High risk of used IP addresses. |
| `multipleDevices` | Multiple devices were used. |
| `multipleMobileDevices` | Multiple mobile devices were used. |
| `lengthySession` | The session is too long. |
| `quickSession` | The session was quick, probably automation. |
| `failedSessionContinuation` | The session was interrupted. |
| `distantIpLocations` | Login from different and distant IP addresses for a short time interval. |
| `thirdPartyLinkAccess` | Link access via external source, e.g. WhatsApp or Telegram |
| `riskySessionContinuation` | Continuation of the session from a risky IP when link was failed to be opened or accessed from a messanger |
| `nightTimeActivity` | Activity was performed during night hours (00:00–06:00) in the client's timezone. |
| `manyApplicantsSameDevice` | Device was used by multiple applicants |

### <a name="AntifraudDeviceCheckRiskLabel"></a>`Elements of applicant.riskLabels.deviceCheck`

| Value | Description |
| --- | --- |
| `badBot` |  |
| `tampering` |  |
| `virtualMachine` |  |
| `privacySettingsMode` |  |
| `factoryReset` |  |
| `rooted` |  |
| `emulator` |  |
| `clonedApp` |  |
| `jailbroken` |  |
| `fridaTool` |  |
| `locationSpoofing` |  |
| `mitmAttack` |  |
| `goodBot` |  |
| `incognito` |  |
| `developerTools` |  |
| `highActivity` |  |
| `adblock` |  |

### <a name="CrossCheckRiskLabel"></a>`Elements of applicant.riskLabels.crossCheck`

| Value | Description |
| --- | --- |
| `diverseIdDocCountries` | ID documents issued in different countries. |
| `manyAccountDuplicates` | Lots of account duplicates are created. |
| `accountsInManyServices` | The same account is registered in different services. |
| `addressCountryVsIpCountryMismatch` | Phisical address in the country mismatches the country IP address. |
| `idDocCountryVsIpCountryMismatch` | ID document country mismatches the country IP address. |
| `exifCountryVsIdDocCountryOrIpCountryMismatch` | The country detected by EXIF mismatches either the document country or the country IP address. |
| `ipLocationVsTimezoneMismatch` | Checks whether ip location timezone different from the browser timezone |
| `browserLanguageMismatch` | Language of the browser does not match the language of the country IP address or id doc |
| `emailDomainCountryMismatch` | Email domain mismatches known countries for applicants |
| `strongLinkToFraudulentApplicants` | Applicant is strongly linked (Fraud Networks, Duplicate Search) to other applicants rejected for fraud |
| `potentialLinkToFraudulentApplicants` | Applicant is potentially linked (Fraud Networks, Duplicate Search) to other applicants rejected for fraud |

### <a name="SelfieRiskLabel"></a>`Elements of applicant.riskLabels.selfie`

| Value | Description |
| --- | --- |
| `asleep` | The person in the selfie is actually asleep. |
| `forced` | The person is coerced into verification @deprecated use #thirdPartyInvolved instead |
| `multipleFaces` | Multiple faces are present. @deprecated use #thirdPartyInvolved instead |
| `estimatedAgeMismatch` | Estimated age mismatches the age in documents. |
| `virtualCameraPresent` | Virtual (a software-based) camera that simulates a physical camera is detected. |
| `manyAttempts` | Numerous attempts of passing a selfie check. |
| `sameFaceWithDifferentData` | Same face on documents with different data. |
| `thirdPartyInvolved` | Suspected third-party involvement, e.g., another person assisting or holding the applicant |
| `phone` | Person is using a phone during the selfie capture process |

### <a name="AmlRiskLabel"></a>`Elements of applicant.riskLabels.aml`

| Value | Description |
| --- | --- |
| `pep` | The screened entity belongs to the PEP (Politically Exposed Person) category. |
| `sanctions` | The screened entity was found in sanctions lists. |
| `terrorism` | The screened entity is suspected of terrorism. |
| `crime` | The screened entity is suspected of criminal activity. |
| `adverseMedia` | The compromising published information that is related to the user was found in the media. |
| `fitnessProbity` | The screened entity does not comply with Fitness and Probity regime. The core function of the Fitness and Probity Regime is to ensure that individuals in key and customer facing positions are competent and capable |

### <a name="PersonRiskLabel"></a>`Elements of applicant.riskLabels.person`

| Value | Description |
| --- | --- |
| `famousPerson` | The user is supposedly a famous person. |
| `strangeName` | The user has a strange name that does not seem to be a real one. |
| `noPhoneNamesFromWebServices` | No phone names are found in web services. |
| `phoneNameMismatchFromWebServices` | Name mismatch with the names associated with the phone number. |
| `noEmailNamesFromWebServices` | No email names are found in web services. |
| `emailNameMismatchFromWebServices` | Name mismatch with the names associated with the email address. |
| `manyUniquePersonsLinkedToContactData` | The contact data (email or phone) is linked to an anomalously large number of distinct unrelated identities, indicating potential large-scale fake identity creation or multi-accounting. |

### <a name="CompanyRiskLabel"></a>`Elements of applicant.riskLabels.company`

| Value | Description |
| --- | --- |
| `companyAdditionalDataNotFound` | Additional company fields are absent in the database |
| `companyDataMismatch` | Mismatch of additional company fields in the database |
| `companyDocumentMissedRequiredField` | If a field is required for the doc type but missed Required fields: CompanyCrossCheckHelper#REQUIRED_FIELDS ArbitraryDoc config: KybArbitraryDocOcrMapping |
| `companyDocumentDataMismatch` | Some field on the document doesn't match the database ArbitraryDoc config: KybArbitraryDocOcrMapping |
| `companyOwnershipDataNotFound` | Company Ownership data (Info on Persons with significant control) is absent in the reference database. |
| `companyBeneficialOwnershipDataNotFound` | Company Ultimate Beneficial Ownership data is absent in the reference database |
| `companyOfficersDataNotFound` | Company Officers data is absent in the reference database |
| `companyDocumentGraphicEditor` | Company document metadata contains blacklisted graphic editors |
| `companyAddressGeoRegistryMismatch` |  |
| `companyAssociatedPartyDataMismatch` | Some of non-critical provided beneficiary data (country, shareSize) does not match the database |
| `companyHasBeneficiaryRejected` | One (or more) of the beneficiaries got final rejection. Commonly used with disabled auto-rejection in GS. KybIntegrationSettings#rejectCompanyWhenBeneficiaryRejected |

### <a name="ApplicantAssessmentResultExpressionData"></a>`Elements of applicant.assessment.scores`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ApplicantAssessmentResultExpressionData.tag"></a>`tag` | `String` | Applicant tag. |
| <a name="ApplicantAssessmentResultExpressionData.score"></a>`score` | `Float` | Applicant score. |

### <a name="BackgroundCheckViolation"></a>`Elements of mrz`

Violations that may occur during:
 <ul>
     <li>cross validation of the applicant and their info, documents</li>
     <li>document validation</li>
 </ul>

| Value | Description |
| --- | --- |
| `BDATE_MISMATCH` |  |
| `ISSUED_DATE_MISMATCH` |  |
| `NAME_MISMATCH` |  |
| `PHONE_MISMATCH` |  |
| `GENDER_MISMATCH` |  |
| `NO_APPLICANT_DATA` |  |
| `COMPANY_REGISTRATION_NUMBER_MISMATCH` |  |
| `TIN_MISMATCH` |  |
| `NOT_ALL_FIELDS_RECOGNIZED` |  |
| `DOC_EXPIRES_SOON` |  |
| `DOC_EXPIRED` |  |
| `EXPIRATION_DATE_MISMATCH` |  |
| `INCONSISTENT_MRZ` |  |
| `MRZ_PARSING_ERROR` |  |
| `BAD_MRZ_DOB` |  |
| `BAD_MRZ_EXP_DATE` |  |
| `BAD_MRZ_NUMBER` |  |
| `MRZ_DATA_MISMATCH` |  |
| `MRZ_NUM_MISMATCH` |  |
| `MRZ_ADDITIONAL_NUMBER_MISMATCH` |  |
| `MRZ_DATE_MISMATCH` |  |
| `MRZ_DOB_MISMATCH` |  |
| `MRZ_ISSUED_DATE_MISMATCH` |  |
| `MRZ_FIRST_ISSUED_DATE_MISMATCH` |  |
| `MRZ_EXPIRY_DATE_MISMATCH` |  |
| `MRZ_NAME_MISMATCH` |  |
| `MRZ_COUNTRY_MISMATCH` |  |
| `MRZ_AUTHORITY_CODE_MISMATCH` |  |
| `IMAGE_SHOULD_BE_MRZ_DOCUMENT_ERROR` |  |
| `IMAGE_SAME_SIDES_ERROR` |  |
| `INCONSISTENT_BARCODE` |  |
| `BARCODE_PARSING_ERROR` |  |
| `BARCODE_DATA_MISMATCH` |  |
| `BARCODE_NUM_MISMATCH` |  |
| `BARCODE_DATE_MISMATCH` |  |
| `BARCODE_NAME_MISMATCH` |  |
| `BARCODE_COUNTRY_MISMATCH` |  |
| `BARCODE_GENDER_MISMATCH` |  |
| `BARCODE_ADDITIONAL_NUMBER_MISMATCH` |  |
| `INVALID_DOC_NUMBER` |  |
| `INVALID_EXPIRATION_DATE` |  |
| `INVALID_ADDITIONAL_NUMBER` |  |
| `BDATE_ADDITIONAL_NUMBER_MISMATCH` |  |
| `BDATE_NUMBER_MISMATCH` |  |
| `GENDER_ADDITIONAL_NUMBER_MISMATCH` |  |
| `NAME_NUMBER_MISMATCH` |  |
| `ADDRESS_MISMATCH` |  |
| `NFC_MRZ_MISMATCH` |  |
| `NFC_CERT_MISMATCH` |  |
| `NFC_INFO_MISSED` |  |
| `DEAD` | Person is marked as dead (used in external bg checks) |
| `PERSON_IS_MINOR` | Person is marked as minor (used in external bg checks) |
| `DOCUMENT_LOST` |  |
| `DATA_NOT_FOUND` |  |
| `FALSE_IDENTITY` |  |
| `FALSE_IDENTITY_DOCUMENT` |  |
| `INVALID_STATUS` |  |
| `SELFIE_MISMATCH` |  |
| `RESTRICTED_LIST_HIT` |  |
| `NOT_ENOUGH_DATA` |  |
| `CATEGORY_MISMATCH` |  |
| `DRIVING_RESTRICTIONS` |  |
| `EXTERNAL_DB_SUSPICIOUS` |  |
| `INVALID_ID_STATUS` |  |
| `VERIFICATION_REQUIREMENTS_NOT_MET` | The database check results don't meet verification requirements. Only used when the database check has some composite/complex requirements (ex. found record is 36 months old or found 2 records that are 6 months old) |
| `AUTHENTICATION_FAILED` |  |
| `ID_NUMBER_MISMATCH` |  |
| `ACCOUNT_TYPE_MISMATCH` |  |
| `ACCOUNT_NOT_FOUND` |  |
| `ACCOUNT_NOT_OPEN` |  |

### <a name="MediaTypeId"></a>`poa.image.mimeType, poa2.image.mimeType`

Created by aspotashev on 12/12/14.

| Value | Description |
| --- | --- |
| `PDF` |  |
| `HEIF` |  |
| `JPEG` |  |
| `PNG` |  |
| `GIF` |  |
| `TIFF` |  |
| `WEBP` |  |
| `JP2` |  |
| `YAML` |  |
| `JSON` |  |
| `XML` |  |
| `BMP` |  |
| `VIDEO` |  |
| `CSV` |  |
| `ZIP` |  |
| `UNKNOWN` |  |

### <a name="AllIpChecksExpressionData"></a>`checks.all.ip`

| Field | Type | Description |
| --- | --- | --- |
| <a name="AllIpChecksExpressionData.ips"></a>`ips` | List of `String`-s |  |
| <a name="AllIpChecksExpressionData.stateCodes"></a>`stateCodes` | List of `String`-s |  |
| <a name="AllIpChecksExpressionData.asnOrgs"></a>`asnOrgs` | List of `String`-s |  |
| <a name="AllIpChecksExpressionData.orgs"></a>`orgs` | List of `String`-s |  |
| <a name="AllIpChecksExpressionData.connectionTypes"></a>`connectionTypes` | List of [`Enum`](#IpConnectionType)-s |  |
| <a name="AllIpChecksExpressionData.countries"></a>`countries` | List of `String`-s | Detected countries from all IP checks (ISO 3166-1 alpha-3) |
| <a name="AllIpChecksExpressionData.vpns"></a>`vpns` | List of [`Enum`](#ImageTestAnswer)-s | VPN answers from all IP checks |
| <a name="AllIpChecksExpressionData.tors"></a>`tors` | List of [`Enum`](#ImageTestAnswer)-s | TOR answers from all IP checks |
| <a name="AllIpChecksExpressionData.riskLevels"></a>`riskLevels` | List of [`Enum`](#ImageTestAnswer)-s | Risk levels from all IP checks |

### <a name="PoaCompanyContactType"></a>`checks.poa.companyType, checks.poa2.companyType`

The main types of companies that issue proof of address documents.
 NB: We have promised our clients that these types will not be changed and no new value can be added
 Subtypes (PoaSubType) are used for detailing. Subtypes can be added, but cannot be removed.

| Value | Description |
| --- | --- |
| `governmentOrganization` |  |
| `utilityProvider` |  |
| `bank` |  |
| `mobileOperator` |  |
| `other` |  |

### <a name="PoaSubType"></a>`subType, Elements of possibleSubTypes`

Extended POA subtypes. New values can be added. Is a separate service: ADVANCED_POA_TYPE_DETECTION

| Value | Description |
| --- | --- |
| `statement` |  |
| `voterRegistration` |  |
| `taxBill` |  |
| `telecom` |  |
| `utilityBill` |  |
| `bankStatement` |  |
| `bankLetter` |  |
| `lease` |  |
| `universityLetter` |  |
| `employmentLetter` |  |

### <a name="BgCheckExtractedExpressionData"></a>`checks.ekyc.extractedData`

| Field | Type | Description |
| --- | --- | --- |
| <a name="BgCheckExtractedExpressionData.crossCheckNameData"></a>`crossCheckNameData` | [`Object`](#CrossCheckNameData) | Data from the document that we use for cross-validation |
| <a name="BgCheckExtractedExpressionData.dob"></a>`dob` | [`Date`](#DateExpressionData) | Date of birth |
| <a name="BgCheckExtractedExpressionData.gender"></a>`gender` | `String` | Gender (M or F) |
| <a name="BgCheckExtractedExpressionData.address"></a>`address` | [`Object`](#AddressExpressionData) | ID Document address |
| <a name="BgCheckExtractedExpressionData.additionalFields"></a>`additionalFields` | [`Object`](#AdditionalFieldsExpressionData) | Additional fields |
| <a name="BgCheckExtractedExpressionData.number"></a>`number` | `String` | Extracted ID document number |

### <a name="CompanyCheckInfoExpressionData"></a>`checks.company.info`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyCheckInfoExpressionData.status"></a>`status` | `String` | Company status. |
| <a name="CompanyCheckInfoExpressionData.type"></a>`type` | `String` | Company type. |
| <a name="CompanyCheckInfoExpressionData.registeredCapitalAmount"></a>`registeredCapitalAmount` | `Object` | Registered capital of the company. |
| <a name="CompanyCheckInfoExpressionData.employeesNumber"></a>`employeesNumber` | `Integer` | Approximate number of employees. |
| <a name="CompanyCheckInfoExpressionData.industryCode"></a>`industryCode` | [`Object`](#IndustryCodeExpressionData) | List of industry codes and descriptions. |
| <a name="CompanyCheckInfoExpressionData.incorporatedOn"></a>`incorporatedOn` | [`Date`](#DateExpressionData) | Date of incorporation. |
| <a name="CompanyCheckInfoExpressionData.startDate"></a>`startDate` | [`Date`](#DateExpressionData) | Start date |
| <a name="CompanyCheckInfoExpressionData.legalForm"></a>`legalForm` | `String` | Company legal form |
| <a name="CompanyCheckInfoExpressionData.licenseInfo"></a>`licenseInfo` | [`Object`](#CompanyLicenseInfoExpressionData) | Company license info. |

### <a name="PaymentSourceInfoExpressionData"></a>`checks.paymentSource.extractedInfo`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PaymentSourceInfoExpressionData.type"></a>`type` | [`Enum`](#PaymentSourceType) | Payment method type |
| <a name="PaymentSourceInfoExpressionData.accountIdentifier"></a>`accountIdentifier` | `String` | Account identifier |
| <a name="PaymentSourceInfoExpressionData.institutionName"></a>`institutionName` | `String` | Name of the institution issued payment method |
| <a name="PaymentSourceInfoExpressionData.issuedDate"></a>`issuedDate` | [`Date`](#DateExpressionData) | Document issue date |

### <a name="PaymentSourceRiskCheckExpressionData"></a>`checks.paymentSource.riskCheck`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PaymentSourceRiskCheckExpressionData.binInfo"></a>`binInfo` | [`Object`](#BinInfoExpressionData) |  |

### <a name="NfcValidationExpressionData"></a>`checks.nfcCheck.validation`

| Field | Type | Description |
| --- | --- | --- |
| <a name="NfcValidationExpressionData.activeAuthenticationPassed"></a>`activeAuthenticationPassed` | `Boolean` |  |
| <a name="NfcValidationExpressionData.certificateSelfCheckPassed"></a>`certificateSelfCheckPassed` | `Boolean` |  |
| <a name="NfcValidationExpressionData.certificateMasterListCheckPassed"></a>`certificateMasterListCheckPassed` | `Boolean` |  |
| <a name="NfcValidationExpressionData.mrzCheckPassed"></a>`mrzCheckPassed` | `Boolean` |  |
| <a name="NfcValidationExpressionData.imageCheckPassed"></a>`imageCheckPassed` | `Boolean` |  |

### <a name="NfcExtractedDataExpressionData"></a>`checks.nfcCheck.extractedData`

| Field | Type | Description |
| --- | --- | --- |
| <a name="NfcExtractedDataExpressionData.mrzInfo"></a>`mrzInfo` | [`Object`](#NfcExtractedDataMrzInfoExpressionData) |  |
| <a name="NfcExtractedDataExpressionData.documentInfo"></a>`documentInfo` | [`Object`](#NfcExtractedDataDocumentInfoExpressionData) |  |
| <a name="NfcExtractedDataExpressionData.verificationData"></a>`verificationData` | [`Object`](#NfcExtractedDataVerificationDataExpressionData) |  |

### <a name="CrossValidationCheckExpressionData"></a>`action.checks.crossValidation`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CrossValidationCheckExpressionData.violations"></a>`violations` | List of `String`-s |  |

### <a name="BeneficiaryStatsExpressionData"></a>`beneficiaryStats`

| Field | Type | Description |
| --- | --- | --- |
| <a name="BeneficiaryStatsExpressionData.rejectLabels"></a>`rejectLabels` | List of `String`-s | Beneficiary applicant reject labels |
| <a name="BeneficiaryStatsExpressionData.tags"></a>`tags` | List of `String`-s | Beneficiary applicant tags |
| <a name="BeneficiaryStatsExpressionData.riskLabels"></a>`riskLabels` | [`Object`](#ApplicantRiskLabels) | Beneficiary applicant risk labels |
| <a name="BeneficiaryStatsExpressionData.counts"></a>`counts` | [`Object`](#BeneficiaryCountsExpressionData) |  |

### <a name="UpcomingDocumentExpirationExpressionData"></a>`upcomingDocumentExpiration`

| Field | Type | Description |
| --- | --- | --- |
| <a name="UpcomingDocumentExpirationExpressionData.idDocType"></a>`idDocType` | `String` | Static value "COMPANY_DOC" for all the Company-related documents |
| <a name="UpcomingDocumentExpirationExpressionData.idDocSubType"></a>`idDocSubType` | `String` | Specific type of company document |
| <a name="UpcomingDocumentExpirationExpressionData.expirationDate"></a>`expirationDate` | [`Date`](#DateExpressionData) | Date of company document expiration |

### <a name="DeviceCheckRiskLabel"></a>`applicant.riskLabels.deviceCheck[].riskLabel`

| Value | Description |
| --- | --- |
| `rooted` |  |
| `emulator` |  |
| `badBot` |  |
| `tampering` |  |
| `clonedApp` |  |
| `jailbroken` |  |
| `fridaTool` |  |
| `virtualMachine` |  |
| `locationSpoofing` |  |
| `mitmAttack` |  |
| `privacySettingsMode` |  |
| `goodBot` |  |
| `incognito` |  |
| `highActivity` |  |
| `developerTools` |  |
| `adblock` |  |
| `factoryReset` |  |

### <a name="IpConnectionType"></a>`Elements of checks.all.ip.connectionTypes`

| Value | Description |
| --- | --- |
| `residential` |  |
| `cellular` |  |
| `business` |  |
| `hosting` |  |
| `government` |  |
| `educational` |  |

### <a name="AdditionalFieldsExpressionData"></a>`checks.ekyc.extractedData.additionalFields`

| Field | Type | Description |
| --- | --- | --- |
| <a name="AdditionalFieldsExpressionData.phone"></a>`phone` | [`Object`](#PhoneExpressionData) |  |

### <a name="IndustryCodeExpressionData"></a>`checks.company.info.industryCode`

| Field | Type | Description |
| --- | --- | --- |
| <a name="IndustryCodeExpressionData.codes"></a>`codes` | List of `String`-s | List of Company industry codes. |
| <a name="IndustryCodeExpressionData.descriptions"></a>`descriptions` | List of `String`-s | List of Industry descriptions. |

### <a name="CompanyLicenseInfoExpressionData"></a>`checks.company.info.licenseInfo`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyLicenseInfoExpressionData.issuedDate"></a>`issuedDate` | [`Date`](#DateExpressionData) | Date of issue. |
| <a name="CompanyLicenseInfoExpressionData.validUntil"></a>`validUntil` | [`Date`](#DateExpressionData) | Date of expiry. |

### <a name="PaymentSourceType"></a>`type`

| Value | Description |
| --- | --- |
| `bankCard` |  |
| `bankStatement` |  |
| `eWallet` |  |
| `cryptoWallet` |  |

### <a name="BinInfoExpressionData"></a>`checks.paymentSource.riskCheck.binInfo`

| Field | Type | Description |
| --- | --- | --- |
| <a name="BinInfoExpressionData.country"></a>`country` | `String` |  |
| <a name="BinInfoExpressionData.issuer"></a>`issuer` | `String` |  |
| <a name="BinInfoExpressionData.brand"></a>`brand` | `String` |  |
| <a name="BinInfoExpressionData.type"></a>`type` | `String` |  |
| <a name="BinInfoExpressionData.prepaid"></a>`prepaid` | `Boolean` |  |
| <a name="BinInfoExpressionData.virtual"></a>`virtual` | `Boolean` |  |
| <a name="BinInfoExpressionData.commercial"></a>`commercial` | `Boolean` |  |

### <a name="NfcExtractedDataMrzInfoExpressionData"></a>`checks.nfcCheck.extractedData.mrzInfo`

| Field | Type | Description |
| --- | --- | --- |
| <a name="NfcExtractedDataMrzInfoExpressionData.fullMrz"></a>`fullMrz` | `String` |  |
| <a name="NfcExtractedDataMrzInfoExpressionData.dateOfExpiration"></a>`dateOfExpiration` | [`Date`](#DateExpressionData) |  |
| <a name="NfcExtractedDataMrzInfoExpressionData.documentNumber"></a>`documentNumber` | `String` |  |
| <a name="NfcExtractedDataMrzInfoExpressionData.issuingState"></a>`issuingState` | `String` |  |
| <a name="NfcExtractedDataMrzInfoExpressionData.nationality"></a>`nationality` | `String` |  |
| <a name="NfcExtractedDataMrzInfoExpressionData.identifier"></a>`identifier` | `String` |  |
| <a name="NfcExtractedDataMrzInfoExpressionData.dob"></a>`dob` | [`Date`](#DateExpressionData) |  |
| <a name="NfcExtractedDataMrzInfoExpressionData.gender"></a>`gender` | `String` |  |

### <a name="NfcExtractedDataDocumentInfoExpressionData"></a>`checks.nfcCheck.extractedData.documentInfo`

| Field | Type | Description |
| --- | --- | --- |
| <a name="NfcExtractedDataDocumentInfoExpressionData.nameOfHolder"></a>`nameOfHolder` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.otherNames"></a>`otherNames` | List of `String`-s |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.personalNumber"></a>`personalNumber` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.fullDateOfBirth"></a>`fullDateOfBirth` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.placeOfBirth"></a>`placeOfBirth` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.permanentAddress"></a>`permanentAddress` | List of `String`-s |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.telephone"></a>`telephone` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.profession"></a>`profession` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.title"></a>`title` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.personalSummary"></a>`personalSummary` | `String` |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.otherValidTDNumbers"></a>`otherValidTDNumbers` | List of `String`-s |  |
| <a name="NfcExtractedDataDocumentInfoExpressionData.custodyInformation"></a>`custodyInformation` | `String` |  |

### <a name="NfcExtractedDataVerificationDataExpressionData"></a>`checks.nfcCheck.extractedData.verificationData`

| Field | Type | Description |
| --- | --- | --- |
| <a name="NfcExtractedDataVerificationDataExpressionData.issuingAuthority"></a>`issuingAuthority` | `String` |  |
| <a name="NfcExtractedDataVerificationDataExpressionData.dateOfIssue"></a>`dateOfIssue` | `String` |  |
| <a name="NfcExtractedDataVerificationDataExpressionData.namesOfOtherPersons"></a>`namesOfOtherPersons` | `String` |  |
| <a name="NfcExtractedDataVerificationDataExpressionData.endorsementsAndObservations"></a>`endorsementsAndObservations` | `String` |  |
| <a name="NfcExtractedDataVerificationDataExpressionData.taxOrExitRequirements"></a>`taxOrExitRequirements` | `String` |  |
| <a name="NfcExtractedDataVerificationDataExpressionData.dateAndTimeOfPersonalization"></a>`dateAndTimeOfPersonalization` | `String` |  |
| <a name="NfcExtractedDataVerificationDataExpressionData.personalizationSystemSerialNumber"></a>`personalizationSystemSerialNumber` | `String` |  |

### <a name="BeneficiaryCountsExpressionData"></a>`counts`

| Field | Type | Description |
| --- | --- | --- |
| <a name="BeneficiaryCountsExpressionData.ubos"></a>`ubos` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.shareholders"></a>`shareholders` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.representatives"></a>`representatives` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.directors"></a>`directors` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.companyOfficers"></a>`companyOfficers` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.investors"></a>`investors` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.secretaries"></a>`secretaries` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.founders"></a>`founders` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.legalAdvisors"></a>`legalAdvisors` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.authorizedSignatories"></a>`authorizedSignatories` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.trusties"></a>`trusties` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.trustBeneficiaries"></a>`trustBeneficiaries` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.trustSettlors"></a>`trustSettlors` | `Integer` |  |
| <a name="BeneficiaryCountsExpressionData.trustProtectors"></a>`trustProtectors` | `Integer` |  |

## Index

- [`applicant`](#WorkflowExpressionContext.applicant).[`allMemberRoles`](#ApplicantExpressionData.allMemberRoles)
- [`applicant`](#WorkflowExpressionContext.applicant).[`lang`](#ApplicantExpressionData.lang)
- [`applicant`](#WorkflowExpressionContext.applicant).[`type`](#ApplicantExpressionData.type)
- [`applicant`](#WorkflowExpressionContext.applicant).[`emailDomain`](#ApplicantExpressionData.emailDomain)
- [`applicant`](#WorkflowExpressionContext.applicant).[`phone`](#ApplicantExpressionData.phone).[`country`](#PhoneExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`phone`](#ApplicantExpressionData.phone).[`number`](#PhoneExpressionData.number)
- [`applicant`](#WorkflowExpressionContext.applicant).[`email`](#ApplicantExpressionData.email)
- [`applicant`](#WorkflowExpressionContext.applicant).[`assessment`](#ApplicantExpressionData.assessment).[`scores["..."]`](#ApplicantAssessmentExpressionData.scores).[`score`](#ApplicantAssessmentResultExpressionData.score)
- [`applicant`](#WorkflowExpressionContext.applicant).[`assessment`](#ApplicantExpressionData.assessment).[`scores["..."]`](#ApplicantAssessmentExpressionData.scores).[`tag`](#ApplicantAssessmentResultExpressionData.tag)
- [`applicant`](#WorkflowExpressionContext.applicant).[`assessment`](#ApplicantExpressionData.assessment).[`totalScore`](#ApplicantAssessmentExpressionData.totalScore)
- [`applicant`](#WorkflowExpressionContext.applicant).[`tags`](#ApplicantExpressionData.tags)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`company`](#ApplicantRiskLabels.company)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`person`](#ApplicantRiskLabels.person)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`aml`](#ApplicantRiskLabels.aml)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`selfie`](#ApplicantRiskLabels.selfie)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`crossCheck`](#ApplicantRiskLabels.crossCheck)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`deviceCheck`](#ApplicantRiskLabels.deviceCheck)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`device`](#ApplicantRiskLabels.device)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`phone`](#ApplicantRiskLabels.phone)
- [`applicant`](#WorkflowExpressionContext.applicant).[`riskLabels`](#ApplicantExpressionData.riskLabels).[`email`](#ApplicantRiskLabels.email)
- [`applicant`](#WorkflowExpressionContext.applicant).[`metadata`](#ApplicantExpressionData.metadata)
- [`applicant`](#WorkflowExpressionContext.applicant).[`derivatives`](#ApplicantExpressionData.derivatives).[`estimatedAge`](#ApplicantDerivatives.estimatedAge)
- [`applicant`](#WorkflowExpressionContext.applicant).[`sourceKey`](#ApplicantExpressionData.sourceKey)
- [`applicant`](#WorkflowExpressionContext.applicant).[`review`](#ApplicantExpressionData.review).[`buttonIds`](#InspectionReviewExpressionData.buttonIds)
- [`applicant`](#WorkflowExpressionContext.applicant).[`review`](#ApplicantExpressionData.review).[`rejectLabels`](#InspectionReviewExpressionData.rejectLabels)
- [`applicant`](#WorkflowExpressionContext.applicant).[`review`](#ApplicantExpressionData.review).[`attemptCnt`](#InspectionReviewExpressionData.attemptCnt)
- [`applicant`](#WorkflowExpressionContext.applicant).[`review`](#ApplicantExpressionData.review).[`levelName`](#InspectionReviewExpressionData.levelName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`phone`](#ApplicantInfoExpressionData.phone).[`country`](#PhoneExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`phone`](#ApplicantInfoExpressionData.phone).[`number`](#PhoneExpressionData.number)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`tin`](#ApplicantInfoExpressionData.tin)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`tinCountries`](#ApplicantInfoExpressionData.tinCountries)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`idDocSubType`](#UpcomingDocumentExpirationExpressionData.idDocSubType)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`idDocType`](#UpcomingDocumentExpirationExpressionData.idDocType)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustProtectors`](#BeneficiaryCountsExpressionData.trustProtectors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustSettlors`](#BeneficiaryCountsExpressionData.trustSettlors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustBeneficiaries`](#BeneficiaryCountsExpressionData.trustBeneficiaries)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trusties`](#BeneficiaryCountsExpressionData.trusties)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`authorizedSignatories`](#BeneficiaryCountsExpressionData.authorizedSignatories)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`legalAdvisors`](#BeneficiaryCountsExpressionData.legalAdvisors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`founders`](#BeneficiaryCountsExpressionData.founders)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`secretaries`](#BeneficiaryCountsExpressionData.secretaries)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`investors`](#BeneficiaryCountsExpressionData.investors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`companyOfficers`](#BeneficiaryCountsExpressionData.companyOfficers)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`directors`](#BeneficiaryCountsExpressionData.directors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`representatives`](#BeneficiaryCountsExpressionData.representatives)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`shareholders`](#BeneficiaryCountsExpressionData.shareholders)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`ubos`](#BeneficiaryCountsExpressionData.ubos)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`company`](#ApplicantRiskLabels.company)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`person`](#ApplicantRiskLabels.person)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`aml`](#ApplicantRiskLabels.aml)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`selfie`](#ApplicantRiskLabels.selfie)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`crossCheck`](#ApplicantRiskLabels.crossCheck)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`deviceCheck`](#ApplicantRiskLabels.deviceCheck)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`device`](#ApplicantRiskLabels.device)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`phone`](#ApplicantRiskLabels.phone)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`email`](#ApplicantRiskLabels.email)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`tags`](#BeneficiaryStatsExpressionData.tags)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`rejectLabels`](#BeneficiaryStatsExpressionData.rejectLabels)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`ownershipStructureDepth`](#CompanyInfoExpressionData.ownershipStructureDepth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`skippedTypes`](#CompanyInfoExpressionData.skippedTypes)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiallyHeld`](#CompanyInfoExpressionData.beneficiallyHeld)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`noShareholders`](#CompanyInfoExpressionData.noShareholders)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`noUBOs`](#CompanyInfoExpressionData.noUBOs)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`website`](#CompanyInfoExpressionData.website)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`taxId`](#CompanyInfoExpressionData.taxId)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`phone`](#CompanyInfoExpressionData.phone)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`email`](#CompanyInfoExpressionData.email)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporatedOn`](#CompanyInfoExpressionData.incorporatedOn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`registrationLocation`](#CompanyInfoExpressionData.registrationLocation)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`postalAddress`](#CompanyInfoExpressionData.postalAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`legalAddress`](#CompanyInfoExpressionData.legalAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`leiCode`](#CompanyInfoExpressionData.leiCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`registrationNumber`](#CompanyInfoExpressionData.registrationNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`companyName`](#CompanyInfoExpressionData.companyName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`legalForm`](#CompanyInfoExpressionData.legalForm)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`type`](#CompanyInfoExpressionData.type)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`country`](#CompanyInfoExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`age`](#ApplicantInfoExpressionData.age)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`residenceCountry`](#ApplicantInfoExpressionData.residenceCountry)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`taxResidenceCountry`](#ApplicantInfoExpressionData.taxResidenceCountry)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`nationality`](#ApplicantInfoExpressionData.nationality)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`gender`](#ApplicantInfoExpressionData.gender)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`lastNameEn`](#ApplicantInfoExpressionData.lastNameEn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`lastName`](#ApplicantInfoExpressionData.lastName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`middleNameEn`](#ApplicantInfoExpressionData.middleNameEn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`middleName`](#ApplicantInfoExpressionData.middleName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`firstNameEn`](#ApplicantInfoExpressionData.firstNameEn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`firstName`](#ApplicantInfoExpressionData.firstName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`countryOfBirth`](#ApplicantInfoExpressionData.countryOfBirth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`country`](#ApplicantInfoExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckParentName2`](#ApplicantInfoExpressionData.crossCheckParentName2).[`fullName`](#CrossCheckFullNameData.fullName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckParentName2`](#ApplicantInfoExpressionData.crossCheckParentName2).[`country`](#CrossCheckFullNameData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckParentName1`](#ApplicantInfoExpressionData.crossCheckParentName1).[`fullName`](#CrossCheckFullNameData.fullName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckParentName1`](#ApplicantInfoExpressionData.crossCheckParentName1).[`country`](#CrossCheckFullNameData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fixedInfo`](#ApplicantExpressionData.fixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`phone`](#ApplicantInfoExpressionData.phone).[`country`](#PhoneExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`phone`](#ApplicantInfoExpressionData.phone).[`number`](#PhoneExpressionData.number)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`tin`](#ApplicantInfoExpressionData.tin)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`tinCountries`](#ApplicantInfoExpressionData.tinCountries)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`idDocSubType`](#UpcomingDocumentExpirationExpressionData.idDocSubType)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`idDocType`](#UpcomingDocumentExpirationExpressionData.idDocType)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustProtectors`](#BeneficiaryCountsExpressionData.trustProtectors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustSettlors`](#BeneficiaryCountsExpressionData.trustSettlors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustBeneficiaries`](#BeneficiaryCountsExpressionData.trustBeneficiaries)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trusties`](#BeneficiaryCountsExpressionData.trusties)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`authorizedSignatories`](#BeneficiaryCountsExpressionData.authorizedSignatories)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`legalAdvisors`](#BeneficiaryCountsExpressionData.legalAdvisors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`founders`](#BeneficiaryCountsExpressionData.founders)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`secretaries`](#BeneficiaryCountsExpressionData.secretaries)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`investors`](#BeneficiaryCountsExpressionData.investors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`companyOfficers`](#BeneficiaryCountsExpressionData.companyOfficers)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`directors`](#BeneficiaryCountsExpressionData.directors)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`representatives`](#BeneficiaryCountsExpressionData.representatives)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`shareholders`](#BeneficiaryCountsExpressionData.shareholders)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`ubos`](#BeneficiaryCountsExpressionData.ubos)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`company`](#ApplicantRiskLabels.company)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`person`](#ApplicantRiskLabels.person)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`aml`](#ApplicantRiskLabels.aml)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`selfie`](#ApplicantRiskLabels.selfie)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`crossCheck`](#ApplicantRiskLabels.crossCheck)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`deviceCheck`](#ApplicantRiskLabels.deviceCheck)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`device`](#ApplicantRiskLabels.device)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`phone`](#ApplicantRiskLabels.phone)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`email`](#ApplicantRiskLabels.email)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`tags`](#BeneficiaryStatsExpressionData.tags)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`rejectLabels`](#BeneficiaryStatsExpressionData.rejectLabels)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`ownershipStructureDepth`](#CompanyInfoExpressionData.ownershipStructureDepth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`skippedTypes`](#CompanyInfoExpressionData.skippedTypes)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiallyHeld`](#CompanyInfoExpressionData.beneficiallyHeld)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`noShareholders`](#CompanyInfoExpressionData.noShareholders)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`noUBOs`](#CompanyInfoExpressionData.noUBOs)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`website`](#CompanyInfoExpressionData.website)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`taxId`](#CompanyInfoExpressionData.taxId)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`phone`](#CompanyInfoExpressionData.phone)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`email`](#CompanyInfoExpressionData.email)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporatedOn`](#CompanyInfoExpressionData.incorporatedOn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`registrationLocation`](#CompanyInfoExpressionData.registrationLocation)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`postalAddress`](#CompanyInfoExpressionData.postalAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`legalAddress`](#CompanyInfoExpressionData.legalAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`leiCode`](#CompanyInfoExpressionData.leiCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`registrationNumber`](#CompanyInfoExpressionData.registrationNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`companyName`](#CompanyInfoExpressionData.companyName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`legalForm`](#CompanyInfoExpressionData.legalForm)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`type`](#CompanyInfoExpressionData.type)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`country`](#CompanyInfoExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`street`](#AddressExpressionData.street)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`town`](#AddressExpressionData.town)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`state`](#AddressExpressionData.state)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`address`](#ApplicantInfoExpressionData.address).[`country`](#AddressExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`dob`](#ApplicantInfoExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`dob`](#ApplicantInfoExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`dob`](#ApplicantInfoExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`dob`](#ApplicantInfoExpressionData.dob).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`dob`](#ApplicantInfoExpressionData.dob).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`dob`](#ApplicantInfoExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`dob`](#ApplicantInfoExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`age`](#ApplicantInfoExpressionData.age)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`residenceCountry`](#ApplicantInfoExpressionData.residenceCountry)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`taxResidenceCountry`](#ApplicantInfoExpressionData.taxResidenceCountry)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`nationality`](#ApplicantInfoExpressionData.nationality)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`gender`](#ApplicantInfoExpressionData.gender)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`lastNameEn`](#ApplicantInfoExpressionData.lastNameEn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`lastName`](#ApplicantInfoExpressionData.lastName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`middleNameEn`](#ApplicantInfoExpressionData.middleNameEn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`middleName`](#ApplicantInfoExpressionData.middleName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`firstNameEn`](#ApplicantInfoExpressionData.firstNameEn)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`firstName`](#ApplicantInfoExpressionData.firstName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`countryOfBirth`](#ApplicantInfoExpressionData.countryOfBirth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`country`](#ApplicantInfoExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckParentName2`](#ApplicantInfoExpressionData.crossCheckParentName2).[`fullName`](#CrossCheckFullNameData.fullName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckParentName2`](#ApplicantInfoExpressionData.crossCheckParentName2).[`country`](#CrossCheckFullNameData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckParentName1`](#ApplicantInfoExpressionData.crossCheckParentName1).[`fullName`](#CrossCheckFullNameData.fullName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckParentName1`](#ApplicantInfoExpressionData.crossCheckParentName1).[`country`](#CrossCheckFullNameData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`info`](#ApplicantExpressionData.info).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`countryOfBirth`](#ApplicantExpressionData.countryOfBirth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`country`](#ApplicantExpressionData.country)
- [`applicant`](#WorkflowExpressionContext.applicant).[`fullName`](#ApplicantExpressionData.fullName)
- [`applicant`](#WorkflowExpressionContext.applicant).[`registrationDate`](#ApplicantExpressionData.registrationDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`registrationDate`](#ApplicantExpressionData.registrationDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`registrationDate`](#ApplicantExpressionData.registrationDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`registrationDate`](#ApplicantExpressionData.registrationDate).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`registrationDate`](#ApplicantExpressionData.registrationDate).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`registrationDate`](#ApplicantExpressionData.registrationDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`registrationDate`](#ApplicantExpressionData.registrationDate).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`createdAt`](#ApplicantExpressionData.createdAt).[`ageInDays`](#DateExpressionData.ageInDays)
- [`applicant`](#WorkflowExpressionContext.applicant).[`createdAt`](#ApplicantExpressionData.createdAt).[`ageInYears`](#DateExpressionData.ageInYears)
- [`applicant`](#WorkflowExpressionContext.applicant).[`createdAt`](#ApplicantExpressionData.createdAt).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`applicant`](#WorkflowExpressionContext.applicant).[`createdAt`](#ApplicantExpressionData.createdAt).[`month`](#DateExpressionData.month)
- [`applicant`](#WorkflowExpressionContext.applicant).[`createdAt`](#ApplicantExpressionData.createdAt).[`year`](#DateExpressionData.year)
- [`applicant`](#WorkflowExpressionContext.applicant).[`createdAt`](#ApplicantExpressionData.createdAt).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`applicant`](#WorkflowExpressionContext.applicant).[`createdAt`](#ApplicantExpressionData.createdAt).[`timestamp`](#DateExpressionData.timestamp)
- [`applicant`](#WorkflowExpressionContext.applicant).[`externalUserId`](#ApplicantExpressionData.externalUserId)
- [`applicant`](#WorkflowExpressionContext.applicant).[`id`](#ApplicantExpressionData.id)
- [`poi`](#WorkflowExpressionContext.poi).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi`](#WorkflowExpressionContext.poi).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi`](#WorkflowExpressionContext.poi).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi`](#WorkflowExpressionContext.poi).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`month`](#DateExpressionData.month)
- [`poi`](#WorkflowExpressionContext.poi).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`year`](#DateExpressionData.year)
- [`poi`](#WorkflowExpressionContext.poi).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi`](#WorkflowExpressionContext.poi).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi`](#WorkflowExpressionContext.poi).[`ocrDocTypes`](#PoiExpressionData.ocrDocTypes)
- [`poi`](#WorkflowExpressionContext.poi).[`violations`](#PoiExpressionData.violations).[`barcode`](#DocViolationsExpressionData.barcode)
- [`poi`](#WorkflowExpressionContext.poi).[`violations`](#PoiExpressionData.violations).[`dfr`](#DocViolationsExpressionData.dfr)
- [`poi`](#WorkflowExpressionContext.poi).[`violations`](#PoiExpressionData.violations).[`mrz`](#DocViolationsExpressionData.mrz)
- [`poi`](#WorkflowExpressionContext.poi).[`gender`](#PoiExpressionData.gender)
- [`poi`](#WorkflowExpressionContext.poi).[`fullMrz`](#PoiExpressionData.fullMrz)
- [`poi`](#WorkflowExpressionContext.poi).[`nfc`](#PoiExpressionData.nfc).[`fullMrz`](#NfcInfoExpressionData.fullMrz)
- [`poi`](#WorkflowExpressionContext.poi).[`category`](#PoiExpressionData.category)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`street`](#AddressExpressionData.street)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`town`](#AddressExpressionData.town)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`state`](#AddressExpressionData.state)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`poi`](#WorkflowExpressionContext.poi).[`address`](#PoiExpressionData.address).[`country`](#AddressExpressionData.country)
- [`poi`](#WorkflowExpressionContext.poi).[`metadata`](#PoiExpressionData.metadata)
- [`poi`](#WorkflowExpressionContext.poi).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi`](#WorkflowExpressionContext.poi).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi`](#WorkflowExpressionContext.poi).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi`](#WorkflowExpressionContext.poi).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`month`](#DateExpressionData.month)
- [`poi`](#WorkflowExpressionContext.poi).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`year`](#DateExpressionData.year)
- [`poi`](#WorkflowExpressionContext.poi).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi`](#WorkflowExpressionContext.poi).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi`](#WorkflowExpressionContext.poi).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`seconds`](#TimespanExpressionData.seconds)
- [`poi`](#WorkflowExpressionContext.poi).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`minutes`](#TimespanExpressionData.minutes)
- [`poi`](#WorkflowExpressionContext.poi).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`hours`](#TimespanExpressionData.hours)
- [`poi`](#WorkflowExpressionContext.poi).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`days`](#TimespanExpressionData.days)
- [`poi`](#WorkflowExpressionContext.poi).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`millis`](#TimespanExpressionData.millis)
- [`poi`](#WorkflowExpressionContext.poi).[`validUntil`](#PoiExpressionData.validUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi`](#WorkflowExpressionContext.poi).[`validUntil`](#PoiExpressionData.validUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi`](#WorkflowExpressionContext.poi).[`validUntil`](#PoiExpressionData.validUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi`](#WorkflowExpressionContext.poi).[`validUntil`](#PoiExpressionData.validUntil).[`month`](#DateExpressionData.month)
- [`poi`](#WorkflowExpressionContext.poi).[`validUntil`](#PoiExpressionData.validUntil).[`year`](#DateExpressionData.year)
- [`poi`](#WorkflowExpressionContext.poi).[`validUntil`](#PoiExpressionData.validUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi`](#WorkflowExpressionContext.poi).[`validUntil`](#PoiExpressionData.validUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi`](#WorkflowExpressionContext.poi).[`issueAuthorityCode`](#PoiExpressionData.issueAuthorityCode)
- [`poi`](#WorkflowExpressionContext.poi).[`issueAuthority`](#PoiExpressionData.issueAuthority)
- [`poi`](#WorkflowExpressionContext.poi).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi`](#WorkflowExpressionContext.poi).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi`](#WorkflowExpressionContext.poi).[`issuedDate`](#PoiExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi`](#WorkflowExpressionContext.poi).[`issuedDate`](#PoiExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`poi`](#WorkflowExpressionContext.poi).[`issuedDate`](#PoiExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`poi`](#WorkflowExpressionContext.poi).[`issuedDate`](#PoiExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi`](#WorkflowExpressionContext.poi).[`issuedDate`](#PoiExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi`](#WorkflowExpressionContext.poi).[`placeOfBirth`](#PoiExpressionData.placeOfBirth)
- [`poi`](#WorkflowExpressionContext.poi).[`nationality`](#PoiExpressionData.nationality)
- [`poi`](#WorkflowExpressionContext.poi).[`dob`](#PoiExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi`](#WorkflowExpressionContext.poi).[`dob`](#PoiExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi`](#WorkflowExpressionContext.poi).[`dob`](#PoiExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi`](#WorkflowExpressionContext.poi).[`dob`](#PoiExpressionData.dob).[`month`](#DateExpressionData.month)
- [`poi`](#WorkflowExpressionContext.poi).[`dob`](#PoiExpressionData.dob).[`year`](#DateExpressionData.year)
- [`poi`](#WorkflowExpressionContext.poi).[`dob`](#PoiExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi`](#WorkflowExpressionContext.poi).[`dob`](#PoiExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`poi`](#WorkflowExpressionContext.poi).[`additionalNumber`](#PoiExpressionData.additionalNumber)
- [`poi`](#WorkflowExpressionContext.poi).[`number`](#PoiExpressionData.number)
- [`poi`](#WorkflowExpressionContext.poi).[`idDocType`](#PoiExpressionData.idDocType)
- [`poi`](#WorkflowExpressionContext.poi).[`country`](#PoiExpressionData.country)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`country`](#CrossCheckFullNameData.country)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`country`](#CrossCheckFullNameData.country)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`poi`](#WorkflowExpressionContext.poi).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`month`](#DateExpressionData.month)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`year`](#DateExpressionData.year)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi2`](#WorkflowExpressionContext.poi2).[`ocrDocTypes`](#PoiExpressionData.ocrDocTypes)
- [`poi2`](#WorkflowExpressionContext.poi2).[`violations`](#PoiExpressionData.violations).[`barcode`](#DocViolationsExpressionData.barcode)
- [`poi2`](#WorkflowExpressionContext.poi2).[`violations`](#PoiExpressionData.violations).[`dfr`](#DocViolationsExpressionData.dfr)
- [`poi2`](#WorkflowExpressionContext.poi2).[`violations`](#PoiExpressionData.violations).[`mrz`](#DocViolationsExpressionData.mrz)
- [`poi2`](#WorkflowExpressionContext.poi2).[`gender`](#PoiExpressionData.gender)
- [`poi2`](#WorkflowExpressionContext.poi2).[`fullMrz`](#PoiExpressionData.fullMrz)
- [`poi2`](#WorkflowExpressionContext.poi2).[`nfc`](#PoiExpressionData.nfc).[`fullMrz`](#NfcInfoExpressionData.fullMrz)
- [`poi2`](#WorkflowExpressionContext.poi2).[`category`](#PoiExpressionData.category)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`street`](#AddressExpressionData.street)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`town`](#AddressExpressionData.town)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`state`](#AddressExpressionData.state)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`poi2`](#WorkflowExpressionContext.poi2).[`address`](#PoiExpressionData.address).[`country`](#AddressExpressionData.country)
- [`poi2`](#WorkflowExpressionContext.poi2).[`metadata`](#PoiExpressionData.metadata)
- [`poi2`](#WorkflowExpressionContext.poi2).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi2`](#WorkflowExpressionContext.poi2).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi2`](#WorkflowExpressionContext.poi2).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi2`](#WorkflowExpressionContext.poi2).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`month`](#DateExpressionData.month)
- [`poi2`](#WorkflowExpressionContext.poi2).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`year`](#DateExpressionData.year)
- [`poi2`](#WorkflowExpressionContext.poi2).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi2`](#WorkflowExpressionContext.poi2).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`seconds`](#TimespanExpressionData.seconds)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`minutes`](#TimespanExpressionData.minutes)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`hours`](#TimespanExpressionData.hours)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`days`](#TimespanExpressionData.days)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`millis`](#TimespanExpressionData.millis)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validUntil`](#PoiExpressionData.validUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validUntil`](#PoiExpressionData.validUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validUntil`](#PoiExpressionData.validUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validUntil`](#PoiExpressionData.validUntil).[`month`](#DateExpressionData.month)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validUntil`](#PoiExpressionData.validUntil).[`year`](#DateExpressionData.year)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validUntil`](#PoiExpressionData.validUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi2`](#WorkflowExpressionContext.poi2).[`validUntil`](#PoiExpressionData.validUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issueAuthorityCode`](#PoiExpressionData.issueAuthorityCode)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issueAuthority`](#PoiExpressionData.issueAuthority)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issuedDate`](#PoiExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issuedDate`](#PoiExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issuedDate`](#PoiExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issuedDate`](#PoiExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi2`](#WorkflowExpressionContext.poi2).[`issuedDate`](#PoiExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi2`](#WorkflowExpressionContext.poi2).[`placeOfBirth`](#PoiExpressionData.placeOfBirth)
- [`poi2`](#WorkflowExpressionContext.poi2).[`nationality`](#PoiExpressionData.nationality)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dob`](#PoiExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dob`](#PoiExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dob`](#PoiExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dob`](#PoiExpressionData.dob).[`month`](#DateExpressionData.month)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dob`](#PoiExpressionData.dob).[`year`](#DateExpressionData.year)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dob`](#PoiExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi2`](#WorkflowExpressionContext.poi2).[`dob`](#PoiExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`poi2`](#WorkflowExpressionContext.poi2).[`additionalNumber`](#PoiExpressionData.additionalNumber)
- [`poi2`](#WorkflowExpressionContext.poi2).[`number`](#PoiExpressionData.number)
- [`poi2`](#WorkflowExpressionContext.poi2).[`idDocType`](#PoiExpressionData.idDocType)
- [`poi2`](#WorkflowExpressionContext.poi2).[`country`](#PoiExpressionData.country)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`country`](#CrossCheckFullNameData.country)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`country`](#CrossCheckFullNameData.country)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`poi2`](#WorkflowExpressionContext.poi2).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`month`](#DateExpressionData.month)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`year`](#DateExpressionData.year)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi3`](#WorkflowExpressionContext.poi3).[`ocrDocTypes`](#PoiExpressionData.ocrDocTypes)
- [`poi3`](#WorkflowExpressionContext.poi3).[`violations`](#PoiExpressionData.violations).[`barcode`](#DocViolationsExpressionData.barcode)
- [`poi3`](#WorkflowExpressionContext.poi3).[`violations`](#PoiExpressionData.violations).[`dfr`](#DocViolationsExpressionData.dfr)
- [`poi3`](#WorkflowExpressionContext.poi3).[`violations`](#PoiExpressionData.violations).[`mrz`](#DocViolationsExpressionData.mrz)
- [`poi3`](#WorkflowExpressionContext.poi3).[`gender`](#PoiExpressionData.gender)
- [`poi3`](#WorkflowExpressionContext.poi3).[`fullMrz`](#PoiExpressionData.fullMrz)
- [`poi3`](#WorkflowExpressionContext.poi3).[`nfc`](#PoiExpressionData.nfc).[`fullMrz`](#NfcInfoExpressionData.fullMrz)
- [`poi3`](#WorkflowExpressionContext.poi3).[`category`](#PoiExpressionData.category)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`street`](#AddressExpressionData.street)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`town`](#AddressExpressionData.town)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`state`](#AddressExpressionData.state)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`poi3`](#WorkflowExpressionContext.poi3).[`address`](#PoiExpressionData.address).[`country`](#AddressExpressionData.country)
- [`poi3`](#WorkflowExpressionContext.poi3).[`metadata`](#PoiExpressionData.metadata)
- [`poi3`](#WorkflowExpressionContext.poi3).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi3`](#WorkflowExpressionContext.poi3).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi3`](#WorkflowExpressionContext.poi3).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi3`](#WorkflowExpressionContext.poi3).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`month`](#DateExpressionData.month)
- [`poi3`](#WorkflowExpressionContext.poi3).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`year`](#DateExpressionData.year)
- [`poi3`](#WorkflowExpressionContext.poi3).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi3`](#WorkflowExpressionContext.poi3).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`seconds`](#TimespanExpressionData.seconds)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`minutes`](#TimespanExpressionData.minutes)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`hours`](#TimespanExpressionData.hours)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`days`](#TimespanExpressionData.days)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`millis`](#TimespanExpressionData.millis)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validUntil`](#PoiExpressionData.validUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validUntil`](#PoiExpressionData.validUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validUntil`](#PoiExpressionData.validUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validUntil`](#PoiExpressionData.validUntil).[`month`](#DateExpressionData.month)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validUntil`](#PoiExpressionData.validUntil).[`year`](#DateExpressionData.year)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validUntil`](#PoiExpressionData.validUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi3`](#WorkflowExpressionContext.poi3).[`validUntil`](#PoiExpressionData.validUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issueAuthorityCode`](#PoiExpressionData.issueAuthorityCode)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issueAuthority`](#PoiExpressionData.issueAuthority)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issuedDate`](#PoiExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issuedDate`](#PoiExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issuedDate`](#PoiExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issuedDate`](#PoiExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi3`](#WorkflowExpressionContext.poi3).[`issuedDate`](#PoiExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi3`](#WorkflowExpressionContext.poi3).[`placeOfBirth`](#PoiExpressionData.placeOfBirth)
- [`poi3`](#WorkflowExpressionContext.poi3).[`nationality`](#PoiExpressionData.nationality)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dob`](#PoiExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dob`](#PoiExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dob`](#PoiExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dob`](#PoiExpressionData.dob).[`month`](#DateExpressionData.month)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dob`](#PoiExpressionData.dob).[`year`](#DateExpressionData.year)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dob`](#PoiExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi3`](#WorkflowExpressionContext.poi3).[`dob`](#PoiExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`poi3`](#WorkflowExpressionContext.poi3).[`additionalNumber`](#PoiExpressionData.additionalNumber)
- [`poi3`](#WorkflowExpressionContext.poi3).[`number`](#PoiExpressionData.number)
- [`poi3`](#WorkflowExpressionContext.poi3).[`idDocType`](#PoiExpressionData.idDocType)
- [`poi3`](#WorkflowExpressionContext.poi3).[`country`](#PoiExpressionData.country)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`country`](#CrossCheckFullNameData.country)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`country`](#CrossCheckFullNameData.country)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`poi3`](#WorkflowExpressionContext.poi3).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`month`](#DateExpressionData.month)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`year`](#DateExpressionData.year)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dlCategoryBValidUntil`](#PoiExpressionData.dlCategoryBValidUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi4`](#WorkflowExpressionContext.poi4).[`ocrDocTypes`](#PoiExpressionData.ocrDocTypes)
- [`poi4`](#WorkflowExpressionContext.poi4).[`violations`](#PoiExpressionData.violations).[`barcode`](#DocViolationsExpressionData.barcode)
- [`poi4`](#WorkflowExpressionContext.poi4).[`violations`](#PoiExpressionData.violations).[`dfr`](#DocViolationsExpressionData.dfr)
- [`poi4`](#WorkflowExpressionContext.poi4).[`violations`](#PoiExpressionData.violations).[`mrz`](#DocViolationsExpressionData.mrz)
- [`poi4`](#WorkflowExpressionContext.poi4).[`gender`](#PoiExpressionData.gender)
- [`poi4`](#WorkflowExpressionContext.poi4).[`fullMrz`](#PoiExpressionData.fullMrz)
- [`poi4`](#WorkflowExpressionContext.poi4).[`nfc`](#PoiExpressionData.nfc).[`fullMrz`](#NfcInfoExpressionData.fullMrz)
- [`poi4`](#WorkflowExpressionContext.poi4).[`category`](#PoiExpressionData.category)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`street`](#AddressExpressionData.street)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`town`](#AddressExpressionData.town)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`state`](#AddressExpressionData.state)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`poi4`](#WorkflowExpressionContext.poi4).[`address`](#PoiExpressionData.address).[`country`](#AddressExpressionData.country)
- [`poi4`](#WorkflowExpressionContext.poi4).[`metadata`](#PoiExpressionData.metadata)
- [`poi4`](#WorkflowExpressionContext.poi4).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi4`](#WorkflowExpressionContext.poi4).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi4`](#WorkflowExpressionContext.poi4).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi4`](#WorkflowExpressionContext.poi4).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`month`](#DateExpressionData.month)
- [`poi4`](#WorkflowExpressionContext.poi4).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`year`](#DateExpressionData.year)
- [`poi4`](#WorkflowExpressionContext.poi4).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi4`](#WorkflowExpressionContext.poi4).[`firstIssuedDate`](#PoiExpressionData.firstIssuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`seconds`](#TimespanExpressionData.seconds)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`minutes`](#TimespanExpressionData.minutes)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`hours`](#TimespanExpressionData.hours)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`days`](#TimespanExpressionData.days)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validityPeriod`](#PoiExpressionData.validityPeriod).[`millis`](#TimespanExpressionData.millis)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validUntil`](#PoiExpressionData.validUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validUntil`](#PoiExpressionData.validUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validUntil`](#PoiExpressionData.validUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validUntil`](#PoiExpressionData.validUntil).[`month`](#DateExpressionData.month)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validUntil`](#PoiExpressionData.validUntil).[`year`](#DateExpressionData.year)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validUntil`](#PoiExpressionData.validUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi4`](#WorkflowExpressionContext.poi4).[`validUntil`](#PoiExpressionData.validUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issueAuthorityCode`](#PoiExpressionData.issueAuthorityCode)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issueAuthority`](#PoiExpressionData.issueAuthority)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issuedDate`](#PoiExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issuedDate`](#PoiExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issuedDate`](#PoiExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issuedDate`](#PoiExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issuedDate`](#PoiExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi4`](#WorkflowExpressionContext.poi4).[`issuedDate`](#PoiExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poi4`](#WorkflowExpressionContext.poi4).[`placeOfBirth`](#PoiExpressionData.placeOfBirth)
- [`poi4`](#WorkflowExpressionContext.poi4).[`nationality`](#PoiExpressionData.nationality)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dob`](#PoiExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dob`](#PoiExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dob`](#PoiExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dob`](#PoiExpressionData.dob).[`month`](#DateExpressionData.month)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dob`](#PoiExpressionData.dob).[`year`](#DateExpressionData.year)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dob`](#PoiExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poi4`](#WorkflowExpressionContext.poi4).[`dob`](#PoiExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`poi4`](#WorkflowExpressionContext.poi4).[`additionalNumber`](#PoiExpressionData.additionalNumber)
- [`poi4`](#WorkflowExpressionContext.poi4).[`number`](#PoiExpressionData.number)
- [`poi4`](#WorkflowExpressionContext.poi4).[`idDocType`](#PoiExpressionData.idDocType)
- [`poi4`](#WorkflowExpressionContext.poi4).[`country`](#PoiExpressionData.country)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckParentName2`](#PoiExpressionData.crossCheckParentName2).[`country`](#CrossCheckFullNameData.country)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`fullName`](#CrossCheckFullNameData.fullName)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckParentName1`](#PoiExpressionData.crossCheckParentName1).[`country`](#CrossCheckFullNameData.country)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`poi4`](#WorkflowExpressionContext.poi4).[`crossCheckNameData`](#PoiExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`poa`](#WorkflowExpressionContext.poa).[`ocrDocTypes`](#PoaExpressionData.ocrDocTypes)
- [`poa`](#WorkflowExpressionContext.poa).[`violations`](#PoaExpressionData.violations).[`barcode`](#DocViolationsExpressionData.barcode)
- [`poa`](#WorkflowExpressionContext.poa).[`violations`](#PoaExpressionData.violations).[`dfr`](#DocViolationsExpressionData.dfr)
- [`poa`](#WorkflowExpressionContext.poa).[`violations`](#PoaExpressionData.violations).[`mrz`](#DocViolationsExpressionData.mrz)
- [`poa`](#WorkflowExpressionContext.poa).[`gender`](#PoaExpressionData.gender)
- [`poa`](#WorkflowExpressionContext.poa).[`dob`](#PoaExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poa`](#WorkflowExpressionContext.poa).[`dob`](#PoaExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poa`](#WorkflowExpressionContext.poa).[`dob`](#PoaExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poa`](#WorkflowExpressionContext.poa).[`dob`](#PoaExpressionData.dob).[`month`](#DateExpressionData.month)
- [`poa`](#WorkflowExpressionContext.poa).[`dob`](#PoaExpressionData.dob).[`year`](#DateExpressionData.year)
- [`poa`](#WorkflowExpressionContext.poa).[`dob`](#PoaExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poa`](#WorkflowExpressionContext.poa).[`dob`](#PoaExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`poa`](#WorkflowExpressionContext.poa).[`image`](#PoaExpressionData.image).[`mimeType`](#ImageExpressionData.mimeType).[`ext`](#MediaTypeId.ext)
- [`poa`](#WorkflowExpressionContext.poa).[`image`](#PoaExpressionData.image).[`softwareTag`](#ImageExpressionData.softwareTag)
- [`poa`](#WorkflowExpressionContext.poa).[`detectedLanguages`](#PoaExpressionData.detectedLanguages)
- [`poa`](#WorkflowExpressionContext.poa).[`issuedDate`](#PoaExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poa`](#WorkflowExpressionContext.poa).[`issuedDate`](#PoaExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poa`](#WorkflowExpressionContext.poa).[`issuedDate`](#PoaExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poa`](#WorkflowExpressionContext.poa).[`issuedDate`](#PoaExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`poa`](#WorkflowExpressionContext.poa).[`issuedDate`](#PoaExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`poa`](#WorkflowExpressionContext.poa).[`issuedDate`](#PoaExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poa`](#WorkflowExpressionContext.poa).[`issuedDate`](#PoaExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`street`](#AddressExpressionData.street)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`town`](#AddressExpressionData.town)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`state`](#AddressExpressionData.state)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`poa`](#WorkflowExpressionContext.poa).[`address`](#PoaExpressionData.address).[`country`](#AddressExpressionData.country)
- [`poa`](#WorkflowExpressionContext.poa).[`metadata`](#PoaExpressionData.metadata)
- [`poa`](#WorkflowExpressionContext.poa).[`number`](#PoaExpressionData.number)
- [`poa`](#WorkflowExpressionContext.poa).[`idDocType`](#PoaExpressionData.idDocType)
- [`poa`](#WorkflowExpressionContext.poa).[`country`](#PoaExpressionData.country)
- [`poa`](#WorkflowExpressionContext.poa).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`poa`](#WorkflowExpressionContext.poa).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`poa`](#WorkflowExpressionContext.poa).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`poa`](#WorkflowExpressionContext.poa).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`poa`](#WorkflowExpressionContext.poa).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`poa2`](#WorkflowExpressionContext.poa2).[`ocrDocTypes`](#PoaExpressionData.ocrDocTypes)
- [`poa2`](#WorkflowExpressionContext.poa2).[`violations`](#PoaExpressionData.violations).[`barcode`](#DocViolationsExpressionData.barcode)
- [`poa2`](#WorkflowExpressionContext.poa2).[`violations`](#PoaExpressionData.violations).[`dfr`](#DocViolationsExpressionData.dfr)
- [`poa2`](#WorkflowExpressionContext.poa2).[`violations`](#PoaExpressionData.violations).[`mrz`](#DocViolationsExpressionData.mrz)
- [`poa2`](#WorkflowExpressionContext.poa2).[`gender`](#PoaExpressionData.gender)
- [`poa2`](#WorkflowExpressionContext.poa2).[`dob`](#PoaExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poa2`](#WorkflowExpressionContext.poa2).[`dob`](#PoaExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poa2`](#WorkflowExpressionContext.poa2).[`dob`](#PoaExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poa2`](#WorkflowExpressionContext.poa2).[`dob`](#PoaExpressionData.dob).[`month`](#DateExpressionData.month)
- [`poa2`](#WorkflowExpressionContext.poa2).[`dob`](#PoaExpressionData.dob).[`year`](#DateExpressionData.year)
- [`poa2`](#WorkflowExpressionContext.poa2).[`dob`](#PoaExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poa2`](#WorkflowExpressionContext.poa2).[`dob`](#PoaExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`poa2`](#WorkflowExpressionContext.poa2).[`image`](#PoaExpressionData.image).[`mimeType`](#ImageExpressionData.mimeType).[`ext`](#MediaTypeId.ext)
- [`poa2`](#WorkflowExpressionContext.poa2).[`image`](#PoaExpressionData.image).[`softwareTag`](#ImageExpressionData.softwareTag)
- [`poa2`](#WorkflowExpressionContext.poa2).[`detectedLanguages`](#PoaExpressionData.detectedLanguages)
- [`poa2`](#WorkflowExpressionContext.poa2).[`issuedDate`](#PoaExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`poa2`](#WorkflowExpressionContext.poa2).[`issuedDate`](#PoaExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`poa2`](#WorkflowExpressionContext.poa2).[`issuedDate`](#PoaExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`poa2`](#WorkflowExpressionContext.poa2).[`issuedDate`](#PoaExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`poa2`](#WorkflowExpressionContext.poa2).[`issuedDate`](#PoaExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`poa2`](#WorkflowExpressionContext.poa2).[`issuedDate`](#PoaExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`poa2`](#WorkflowExpressionContext.poa2).[`issuedDate`](#PoaExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`street`](#AddressExpressionData.street)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`town`](#AddressExpressionData.town)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`state`](#AddressExpressionData.state)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`poa2`](#WorkflowExpressionContext.poa2).[`address`](#PoaExpressionData.address).[`country`](#AddressExpressionData.country)
- [`poa2`](#WorkflowExpressionContext.poa2).[`metadata`](#PoaExpressionData.metadata)
- [`poa2`](#WorkflowExpressionContext.poa2).[`number`](#PoaExpressionData.number)
- [`poa2`](#WorkflowExpressionContext.poa2).[`idDocType`](#PoaExpressionData.idDocType)
- [`poa2`](#WorkflowExpressionContext.poa2).[`country`](#PoaExpressionData.country)
- [`poa2`](#WorkflowExpressionContext.poa2).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`poa2`](#WorkflowExpressionContext.poa2).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`poa2`](#WorkflowExpressionContext.poa2).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`poa2`](#WorkflowExpressionContext.poa2).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`poa2`](#WorkflowExpressionContext.poa2).[`crossCheckNameData`](#PoaExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`device`](#WorkflowExpressionContext.device).[`info`](#DeviceExpressionData.info).[`browserFullVersion`](#DeviceInfoExpressionData.browserFullVersion)
- [`device`](#WorkflowExpressionContext.device).[`info`](#DeviceExpressionData.info).[`browser`](#DeviceInfoExpressionData.browser)
- [`device`](#WorkflowExpressionContext.device).[`info`](#DeviceExpressionData.info).[`platformVersion`](#DeviceInfoExpressionData.platformVersion)
- [`device`](#WorkflowExpressionContext.device).[`info`](#DeviceExpressionData.info).[`platform`](#DeviceInfoExpressionData.platform)
- [`device`](#WorkflowExpressionContext.device).[`info`](#DeviceExpressionData.info).[`type`](#DeviceInfoExpressionData.type)
- [`device`](#WorkflowExpressionContext.device).[`info`](#DeviceExpressionData.info).[`model`](#DeviceInfoExpressionData.model)
- [`device`](#WorkflowExpressionContext.device).[`info`](#DeviceExpressionData.info).[`make`](#DeviceInfoExpressionData.make)
- [`device`](#WorkflowExpressionContext.device).[`ipStateCode`](#DeviceExpressionData.ipStateCode)
- [`device`](#WorkflowExpressionContext.device).[`ipCountry`](#DeviceExpressionData.ipCountry)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days7`](#DeviceStatsExpressionData.days7).[`deviceIds`](#DevicePeriodStatsExpressionData.deviceIds)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days7`](#DeviceStatsExpressionData.days7).[`riskLabels`](#DevicePeriodStatsExpressionData.riskLabels)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days7`](#DeviceStatsExpressionData.days7).[`sameDeviceApplicantCount`](#DevicePeriodStatsExpressionData.sameDeviceApplicantCount)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days7`](#DeviceStatsExpressionData.days7).[`deviceCount`](#DevicePeriodStatsExpressionData.deviceCount)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days1`](#DeviceStatsExpressionData.days1).[`deviceIds`](#DevicePeriodStatsExpressionData.deviceIds)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days1`](#DeviceStatsExpressionData.days1).[`riskLabels`](#DevicePeriodStatsExpressionData.riskLabels)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days1`](#DeviceStatsExpressionData.days1).[`sameDeviceApplicantCount`](#DevicePeriodStatsExpressionData.sameDeviceApplicantCount)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`days1`](#DeviceStatsExpressionData.days1).[`deviceCount`](#DevicePeriodStatsExpressionData.deviceCount)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`hours1`](#DeviceStatsExpressionData.hours1).[`deviceIds`](#DevicePeriodStatsExpressionData.deviceIds)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`hours1`](#DeviceStatsExpressionData.hours1).[`riskLabels`](#DevicePeriodStatsExpressionData.riskLabels)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`hours1`](#DeviceStatsExpressionData.hours1).[`sameDeviceApplicantCount`](#DevicePeriodStatsExpressionData.sameDeviceApplicantCount)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`hours1`](#DeviceStatsExpressionData.hours1).[`deviceCount`](#DevicePeriodStatsExpressionData.deviceCount)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`minutes5`](#DeviceStatsExpressionData.minutes5).[`deviceIds`](#DevicePeriodStatsExpressionData.deviceIds)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`minutes5`](#DeviceStatsExpressionData.minutes5).[`riskLabels`](#DevicePeriodStatsExpressionData.riskLabels)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`minutes5`](#DeviceStatsExpressionData.minutes5).[`sameDeviceApplicantCount`](#DevicePeriodStatsExpressionData.sameDeviceApplicantCount)
- [`deviceStats`](#WorkflowExpressionContext.deviceStats).[`minutes5`](#DeviceStatsExpressionData.minutes5).[`deviceCount`](#DevicePeriodStatsExpressionData.deviceCount)
- [`questionnaires`](#WorkflowExpressionContext.questionnaires)
- [`clientLists`](#WorkflowExpressionContext.clientLists)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`verificationData`](#NfcExtractedDataExpressionData.verificationData).[`personalizationSystemSerialNumber`](#NfcExtractedDataVerificationDataExpressionData.personalizationSystemSerialNumber)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`verificationData`](#NfcExtractedDataExpressionData.verificationData).[`dateAndTimeOfPersonalization`](#NfcExtractedDataVerificationDataExpressionData.dateAndTimeOfPersonalization)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`verificationData`](#NfcExtractedDataExpressionData.verificationData).[`taxOrExitRequirements`](#NfcExtractedDataVerificationDataExpressionData.taxOrExitRequirements)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`verificationData`](#NfcExtractedDataExpressionData.verificationData).[`endorsementsAndObservations`](#NfcExtractedDataVerificationDataExpressionData.endorsementsAndObservations)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`verificationData`](#NfcExtractedDataExpressionData.verificationData).[`namesOfOtherPersons`](#NfcExtractedDataVerificationDataExpressionData.namesOfOtherPersons)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`verificationData`](#NfcExtractedDataExpressionData.verificationData).[`dateOfIssue`](#NfcExtractedDataVerificationDataExpressionData.dateOfIssue)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`verificationData`](#NfcExtractedDataExpressionData.verificationData).[`issuingAuthority`](#NfcExtractedDataVerificationDataExpressionData.issuingAuthority)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`custodyInformation`](#NfcExtractedDataDocumentInfoExpressionData.custodyInformation)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`otherValidTDNumbers`](#NfcExtractedDataDocumentInfoExpressionData.otherValidTDNumbers)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`personalSummary`](#NfcExtractedDataDocumentInfoExpressionData.personalSummary)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`title`](#NfcExtractedDataDocumentInfoExpressionData.title)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`profession`](#NfcExtractedDataDocumentInfoExpressionData.profession)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`telephone`](#NfcExtractedDataDocumentInfoExpressionData.telephone)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`permanentAddress`](#NfcExtractedDataDocumentInfoExpressionData.permanentAddress)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`placeOfBirth`](#NfcExtractedDataDocumentInfoExpressionData.placeOfBirth)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`fullDateOfBirth`](#NfcExtractedDataDocumentInfoExpressionData.fullDateOfBirth)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`personalNumber`](#NfcExtractedDataDocumentInfoExpressionData.personalNumber)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`otherNames`](#NfcExtractedDataDocumentInfoExpressionData.otherNames)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`documentInfo`](#NfcExtractedDataExpressionData.documentInfo).[`nameOfHolder`](#NfcExtractedDataDocumentInfoExpressionData.nameOfHolder)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`gender`](#NfcExtractedDataMrzInfoExpressionData.gender)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dob`](#NfcExtractedDataMrzInfoExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dob`](#NfcExtractedDataMrzInfoExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dob`](#NfcExtractedDataMrzInfoExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dob`](#NfcExtractedDataMrzInfoExpressionData.dob).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dob`](#NfcExtractedDataMrzInfoExpressionData.dob).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dob`](#NfcExtractedDataMrzInfoExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dob`](#NfcExtractedDataMrzInfoExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`identifier`](#NfcExtractedDataMrzInfoExpressionData.identifier)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`nationality`](#NfcExtractedDataMrzInfoExpressionData.nationality)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`issuingState`](#NfcExtractedDataMrzInfoExpressionData.issuingState)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`documentNumber`](#NfcExtractedDataMrzInfoExpressionData.documentNumber)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dateOfExpiration`](#NfcExtractedDataMrzInfoExpressionData.dateOfExpiration).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dateOfExpiration`](#NfcExtractedDataMrzInfoExpressionData.dateOfExpiration).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dateOfExpiration`](#NfcExtractedDataMrzInfoExpressionData.dateOfExpiration).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dateOfExpiration`](#NfcExtractedDataMrzInfoExpressionData.dateOfExpiration).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dateOfExpiration`](#NfcExtractedDataMrzInfoExpressionData.dateOfExpiration).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dateOfExpiration`](#NfcExtractedDataMrzInfoExpressionData.dateOfExpiration).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`dateOfExpiration`](#NfcExtractedDataMrzInfoExpressionData.dateOfExpiration).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`extractedData`](#NfcCheckExpressionData.extractedData).[`mrzInfo`](#NfcExtractedDataExpressionData.mrzInfo).[`fullMrz`](#NfcExtractedDataMrzInfoExpressionData.fullMrz)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`validation`](#NfcCheckExpressionData.validation).[`imageCheckPassed`](#NfcValidationExpressionData.imageCheckPassed)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`validation`](#NfcCheckExpressionData.validation).[`mrzCheckPassed`](#NfcValidationExpressionData.mrzCheckPassed)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`validation`](#NfcCheckExpressionData.validation).[`certificateMasterListCheckPassed`](#NfcValidationExpressionData.certificateMasterListCheckPassed)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`validation`](#NfcCheckExpressionData.validation).[`certificateSelfCheckPassed`](#NfcValidationExpressionData.certificateSelfCheckPassed)
- [`checks`](#WorkflowExpressionContext.checks).[`nfcCheck`](#BackgroundChecksExpressionData.nfcCheck).[`validation`](#NfcCheckExpressionData.validation).[`activeAuthenticationPassed`](#NfcValidationExpressionData.activeAuthenticationPassed)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`commercial`](#BinInfoExpressionData.commercial)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`virtual`](#BinInfoExpressionData.virtual)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`prepaid`](#BinInfoExpressionData.prepaid)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`type`](#BinInfoExpressionData.type)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`brand`](#BinInfoExpressionData.brand)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`issuer`](#BinInfoExpressionData.issuer)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`country`](#BinInfoExpressionData.country)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`institutionName`](#PaymentSourceInfoExpressionData.institutionName)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`accountIdentifier`](#PaymentSourceInfoExpressionData.accountIdentifier)
- [`checks`](#WorkflowExpressionContext.checks).[`paymentSource`](#BackgroundChecksExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`type`](#PaymentSourceInfoExpressionData.type)
- [`checks`](#WorkflowExpressionContext.checks).[`ip`](#BackgroundChecksExpressionData.ip).[`country`](#IpCheckExpressionData.country)
- [`checks`](#WorkflowExpressionContext.checks).[`companyWatchlist`](#BackgroundChecksExpressionData.companyWatchlist).[`tags`](#CompanyWatchlistCheckExpressionData.tags)
- [`checks`](#WorkflowExpressionContext.checks).[`companyWatchlist`](#BackgroundChecksExpressionData.companyWatchlist).[`matchStatuses`](#CompanyWatchlistCheckExpressionData.matchStatuses)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`tags`](#PersonWatchlistCheckExpressionData.tags)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingUpdatedAt`](#PersonWatchlistCheckExpressionData.ongoingUpdatedAt).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingUpdatedAt`](#PersonWatchlistCheckExpressionData.ongoingUpdatedAt).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingUpdatedAt`](#PersonWatchlistCheckExpressionData.ongoingUpdatedAt).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingUpdatedAt`](#PersonWatchlistCheckExpressionData.ongoingUpdatedAt).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingUpdatedAt`](#PersonWatchlistCheckExpressionData.ongoingUpdatedAt).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingUpdatedAt`](#PersonWatchlistCheckExpressionData.ongoingUpdatedAt).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingUpdatedAt`](#PersonWatchlistCheckExpressionData.ongoingUpdatedAt).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`ongoingMatchStatuses`](#PersonWatchlistCheckExpressionData.ongoingMatchStatuses)
- [`checks`](#WorkflowExpressionContext.checks).[`personWatchlist`](#BackgroundChecksExpressionData.personWatchlist).[`matchStatuses`](#PersonWatchlistCheckExpressionData.matchStatuses)
- [`checks`](#WorkflowExpressionContext.checks).[`customDataSources["..."]`](#BackgroundChecksExpressionData.customDataSources).[`output`](#CustomDataSourceExpressionData.output)
- [`checks`](#WorkflowExpressionContext.checks).[`customDataSources["..."]`](#BackgroundChecksExpressionData.customDataSources).[`success`](#CustomDataSourceExpressionData.success)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`validUntil`](#CompanyLicenseInfoExpressionData.validUntil).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`validUntil`](#CompanyLicenseInfoExpressionData.validUntil).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`validUntil`](#CompanyLicenseInfoExpressionData.validUntil).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`validUntil`](#CompanyLicenseInfoExpressionData.validUntil).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`validUntil`](#CompanyLicenseInfoExpressionData.validUntil).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`validUntil`](#CompanyLicenseInfoExpressionData.validUntil).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`validUntil`](#CompanyLicenseInfoExpressionData.validUntil).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`issuedDate`](#CompanyLicenseInfoExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`issuedDate`](#CompanyLicenseInfoExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`issuedDate`](#CompanyLicenseInfoExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`issuedDate`](#CompanyLicenseInfoExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`issuedDate`](#CompanyLicenseInfoExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`issuedDate`](#CompanyLicenseInfoExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`licenseInfo`](#CompanyCheckInfoExpressionData.licenseInfo).[`issuedDate`](#CompanyLicenseInfoExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`legalForm`](#CompanyCheckInfoExpressionData.legalForm)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`startDate`](#CompanyCheckInfoExpressionData.startDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`startDate`](#CompanyCheckInfoExpressionData.startDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`startDate`](#CompanyCheckInfoExpressionData.startDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`startDate`](#CompanyCheckInfoExpressionData.startDate).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`startDate`](#CompanyCheckInfoExpressionData.startDate).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`startDate`](#CompanyCheckInfoExpressionData.startDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`startDate`](#CompanyCheckInfoExpressionData.startDate).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`incorporatedOn`](#CompanyCheckInfoExpressionData.incorporatedOn).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`incorporatedOn`](#CompanyCheckInfoExpressionData.incorporatedOn).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`incorporatedOn`](#CompanyCheckInfoExpressionData.incorporatedOn).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`incorporatedOn`](#CompanyCheckInfoExpressionData.incorporatedOn).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`incorporatedOn`](#CompanyCheckInfoExpressionData.incorporatedOn).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`incorporatedOn`](#CompanyCheckInfoExpressionData.incorporatedOn).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`incorporatedOn`](#CompanyCheckInfoExpressionData.incorporatedOn).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`industryCode`](#CompanyCheckInfoExpressionData.industryCode).[`descriptions`](#IndustryCodeExpressionData.descriptions)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`industryCode`](#CompanyCheckInfoExpressionData.industryCode).[`codes`](#IndustryCodeExpressionData.codes)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`employeesNumber`](#CompanyCheckInfoExpressionData.employeesNumber)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`registeredCapitalAmount`](#CompanyCheckInfoExpressionData.registeredCapitalAmount)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`type`](#CompanyCheckInfoExpressionData.type)
- [`checks`](#WorkflowExpressionContext.checks).[`company`](#BackgroundChecksExpressionData.company).[`info`](#CompanyCheckExpressionData.info).[`status`](#CompanyCheckInfoExpressionData.status)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`violations`](#EkycCheckExpressionData.violations)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`number`](#BgCheckExtractedExpressionData.number)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`additionalFields`](#BgCheckExtractedExpressionData.additionalFields).[`phone`](#AdditionalFieldsExpressionData.phone).[`country`](#PhoneExpressionData.country)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`additionalFields`](#BgCheckExtractedExpressionData.additionalFields).[`phone`](#AdditionalFieldsExpressionData.phone).[`number`](#PhoneExpressionData.number)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`street`](#AddressExpressionData.street)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`town`](#AddressExpressionData.town)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`state`](#AddressExpressionData.state)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`address`](#BgCheckExtractedExpressionData.address).[`country`](#AddressExpressionData.country)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`gender`](#BgCheckExtractedExpressionData.gender)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`dob`](#BgCheckExtractedExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`dob`](#BgCheckExtractedExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`dob`](#BgCheckExtractedExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`dob`](#BgCheckExtractedExpressionData.dob).[`month`](#DateExpressionData.month)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`dob`](#BgCheckExtractedExpressionData.dob).[`year`](#DateExpressionData.year)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`dob`](#BgCheckExtractedExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`dob`](#BgCheckExtractedExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`crossCheckNameData`](#BgCheckExtractedExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`crossCheckNameData`](#BgCheckExtractedExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`crossCheckNameData`](#BgCheckExtractedExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`crossCheckNameData`](#BgCheckExtractedExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`checks`](#WorkflowExpressionContext.checks).[`ekyc`](#BackgroundChecksExpressionData.ekyc).[`extractedData`](#EkycCheckExpressionData.extractedData).[`crossCheckNameData`](#BgCheckExtractedExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`checks`](#WorkflowExpressionContext.checks).[`poa2`](#BackgroundChecksExpressionData.poa2).[`unconventionalProvider`](#PoaCheckExpressionData.unconventionalProvider)
- [`checks`](#WorkflowExpressionContext.checks).[`poa2`](#BackgroundChecksExpressionData.poa2).[`companyType`](#PoaCheckExpressionData.companyType).[`possibleSubTypes`](#PoaCompanyContactType.possibleSubTypes)
- [`checks`](#WorkflowExpressionContext.checks).[`poa`](#BackgroundChecksExpressionData.poa).[`unconventionalProvider`](#PoaCheckExpressionData.unconventionalProvider)
- [`checks`](#WorkflowExpressionContext.checks).[`poa`](#BackgroundChecksExpressionData.poa).[`companyType`](#PoaCheckExpressionData.companyType).[`possibleSubTypes`](#PoaCompanyContactType.possibleSubTypes)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`riskLevels`](#AllIpChecksExpressionData.riskLevels)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`tors`](#AllIpChecksExpressionData.tors)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`vpns`](#AllIpChecksExpressionData.vpns)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`countries`](#AllIpChecksExpressionData.countries)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`connectionTypes`](#AllIpChecksExpressionData.connectionTypes)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`orgs`](#AllIpChecksExpressionData.orgs)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`asnOrgs`](#AllIpChecksExpressionData.asnOrgs)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`stateCodes`](#AllIpChecksExpressionData.stateCodes)
- [`checks`](#WorkflowExpressionContext.checks).[`all`](#BackgroundChecksExpressionData.all).[`ip`](#AllBackgroundChecksExpressionData.ip).[`ips`](#AllIpChecksExpressionData.ips)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`commercial`](#BinInfoExpressionData.commercial)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`virtual`](#BinInfoExpressionData.virtual)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`prepaid`](#BinInfoExpressionData.prepaid)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`type`](#BinInfoExpressionData.type)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`brand`](#BinInfoExpressionData.brand)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`issuer`](#BinInfoExpressionData.issuer)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`riskCheck`](#PaymentSourceCheckInfoExpressionData.riskCheck).[`binInfo`](#PaymentSourceRiskCheckExpressionData.binInfo).[`country`](#BinInfoExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`institutionName`](#PaymentSourceInfoExpressionData.institutionName)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`accountIdentifier`](#PaymentSourceInfoExpressionData.accountIdentifier)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`paymentSource`](#BackgroundChecksActionExpressionData.paymentSource).[`extractedInfo`](#PaymentSourceCheckInfoExpressionData.extractedInfo).[`type`](#PaymentSourceInfoExpressionData.type)
- [`action`](#WorkflowExpressionContext.action).[`checks`](#ApplicantActionExpressionData.checks).[`crossValidation`](#BackgroundChecksActionExpressionData.crossValidation).[`violations`](#CrossValidationCheckExpressionData.violations)
- [`action`](#WorkflowExpressionContext.action).[`questionnaires`](#ApplicantActionExpressionData.questionnaires)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`phone`](#ApplicantInfoExpressionData.phone).[`country`](#PhoneExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`phone`](#ApplicantInfoExpressionData.phone).[`number`](#PhoneExpressionData.number)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`tin`](#ApplicantInfoExpressionData.tin)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`tinCountries`](#ApplicantInfoExpressionData.tinCountries)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`month`](#DateExpressionData.month)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`year`](#DateExpressionData.year)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`expirationDate`](#UpcomingDocumentExpirationExpressionData.expirationDate).[`timestamp`](#DateExpressionData.timestamp)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`idDocSubType`](#UpcomingDocumentExpirationExpressionData.idDocSubType)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`upcomingDocumentExpiration`](#CompanyInfoExpressionData.upcomingDocumentExpiration).[`idDocType`](#UpcomingDocumentExpirationExpressionData.idDocType)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustProtectors`](#BeneficiaryCountsExpressionData.trustProtectors)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustSettlors`](#BeneficiaryCountsExpressionData.trustSettlors)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trustBeneficiaries`](#BeneficiaryCountsExpressionData.trustBeneficiaries)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`trusties`](#BeneficiaryCountsExpressionData.trusties)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`authorizedSignatories`](#BeneficiaryCountsExpressionData.authorizedSignatories)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`legalAdvisors`](#BeneficiaryCountsExpressionData.legalAdvisors)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`founders`](#BeneficiaryCountsExpressionData.founders)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`secretaries`](#BeneficiaryCountsExpressionData.secretaries)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`investors`](#BeneficiaryCountsExpressionData.investors)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`companyOfficers`](#BeneficiaryCountsExpressionData.companyOfficers)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`directors`](#BeneficiaryCountsExpressionData.directors)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`representatives`](#BeneficiaryCountsExpressionData.representatives)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`shareholders`](#BeneficiaryCountsExpressionData.shareholders)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`counts`](#BeneficiaryStatsExpressionData.counts).[`ubos`](#BeneficiaryCountsExpressionData.ubos)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`company`](#ApplicantRiskLabels.company)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`person`](#ApplicantRiskLabels.person)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`aml`](#ApplicantRiskLabels.aml)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`selfie`](#ApplicantRiskLabels.selfie)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`crossCheck`](#ApplicantRiskLabels.crossCheck)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`deviceCheck`](#ApplicantRiskLabels.deviceCheck)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`device`](#ApplicantRiskLabels.device)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`phone`](#ApplicantRiskLabels.phone)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`riskLabels`](#BeneficiaryStatsExpressionData.riskLabels).[`email`](#ApplicantRiskLabels.email)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`tags`](#BeneficiaryStatsExpressionData.tags)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiaryStats`](#CompanyInfoExpressionData.beneficiaryStats).[`rejectLabels`](#BeneficiaryStatsExpressionData.rejectLabels)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`ownershipStructureDepth`](#CompanyInfoExpressionData.ownershipStructureDepth)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`skippedTypes`](#CompanyInfoExpressionData.skippedTypes)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`beneficiallyHeld`](#CompanyInfoExpressionData.beneficiallyHeld)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`noShareholders`](#CompanyInfoExpressionData.noShareholders)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`noUBOs`](#CompanyInfoExpressionData.noUBOs)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`website`](#CompanyInfoExpressionData.website)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`taxId`](#CompanyInfoExpressionData.taxId)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`phone`](#CompanyInfoExpressionData.phone)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`email`](#CompanyInfoExpressionData.email)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`month`](#DateExpressionData.month)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`year`](#DateExpressionData.year)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporationDate`](#CompanyInfoExpressionData.incorporationDate).[`timestamp`](#DateExpressionData.timestamp)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`incorporatedOn`](#CompanyInfoExpressionData.incorporatedOn)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`registrationLocation`](#CompanyInfoExpressionData.registrationLocation)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`postalAddress`](#CompanyInfoExpressionData.postalAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`legalAddress`](#CompanyInfoExpressionData.legalAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`address`](#CompanyInfoExpressionData.address).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`leiCode`](#CompanyInfoExpressionData.leiCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`registrationNumber`](#CompanyInfoExpressionData.registrationNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`companyName`](#CompanyInfoExpressionData.companyName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`legalForm`](#CompanyInfoExpressionData.legalForm)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`type`](#CompanyInfoExpressionData.type)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`companyInfo`](#ApplicantInfoExpressionData.companyInfo).[`country`](#CompanyInfoExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfIdentity`](#ApplicantInfoAddressesExpressionData.proofOfIdentity).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`proofOfAddress`](#ApplicantInfoAddressesExpressionData.proofOfAddress).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`externalDb`](#ApplicantInfoAddressesExpressionData.externalDb).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`gps`](#ApplicantInfoAddressesExpressionData.gps).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`autoComplete`](#ApplicantInfoAddressesExpressionData.autoComplete).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`addresses`](#ApplicantInfoExpressionData.addresses).[`manual`](#ApplicantInfoAddressesExpressionData.manual).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`flatNumber`](#AddressExpressionData.flatNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`buildingNumber`](#AddressExpressionData.buildingNumber)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`buildingName`](#AddressExpressionData.buildingName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`postCode`](#AddressExpressionData.postCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`subStreet`](#AddressExpressionData.subStreet)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`street`](#AddressExpressionData.street)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`town`](#AddressExpressionData.town)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`stateCode`](#AddressExpressionData.stateCode)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`state`](#AddressExpressionData.state)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`formattedAddress`](#AddressExpressionData.formattedAddress)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`address`](#ApplicantInfoExpressionData.address).[`country`](#AddressExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`ageInDays`](#DateExpressionData.ageInDays)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`ageInYears`](#DateExpressionData.ageInYears)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`month`](#DateExpressionData.month)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`year`](#DateExpressionData.year)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`dob`](#ApplicantInfoExpressionData.dob).[`timestamp`](#DateExpressionData.timestamp)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`age`](#ApplicantInfoExpressionData.age)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`residenceCountry`](#ApplicantInfoExpressionData.residenceCountry)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`taxResidenceCountry`](#ApplicantInfoExpressionData.taxResidenceCountry)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`nationality`](#ApplicantInfoExpressionData.nationality)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`gender`](#ApplicantInfoExpressionData.gender)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`lastNameEn`](#ApplicantInfoExpressionData.lastNameEn)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`lastName`](#ApplicantInfoExpressionData.lastName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`middleNameEn`](#ApplicantInfoExpressionData.middleNameEn)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`middleName`](#ApplicantInfoExpressionData.middleName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`firstNameEn`](#ApplicantInfoExpressionData.firstNameEn)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`firstName`](#ApplicantInfoExpressionData.firstName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`countryOfBirth`](#ApplicantInfoExpressionData.countryOfBirth)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`country`](#ApplicantInfoExpressionData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckParentName2`](#ApplicantInfoExpressionData.crossCheckParentName2).[`fullName`](#CrossCheckFullNameData.fullName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckParentName2`](#ApplicantInfoExpressionData.crossCheckParentName2).[`country`](#CrossCheckFullNameData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckParentName1`](#ApplicantInfoExpressionData.crossCheckParentName1).[`fullName`](#CrossCheckFullNameData.fullName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckParentName1`](#ApplicantInfoExpressionData.crossCheckParentName1).[`country`](#CrossCheckFullNameData.country)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`aliasName`](#CrossCheckNameData.aliasName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`lastName`](#CrossCheckNameData.lastName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`middleName`](#CrossCheckNameData.middleName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`firstName`](#CrossCheckNameData.firstName)
- [`action`](#WorkflowExpressionContext.action).[`actionFixedInfo`](#ApplicantActionExpressionData.actionFixedInfo).[`crossCheckNameData`](#ApplicantInfoExpressionData.crossCheckNameData).[`country`](#CrossCheckNameData.country)
- [`action`](#WorkflowExpressionContext.action).[`metadata`](#ApplicantActionExpressionData.metadata)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`institutionName`](#PaymentSourceInfoExpressionData.institutionName)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`accountIdentifier`](#PaymentSourceInfoExpressionData.accountIdentifier)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`info`](#PaymentSourceExpressionData.info).[`type`](#PaymentSourceInfoExpressionData.type)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInDays`](#DateExpressionData.ageInDays)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`ageInYears`](#DateExpressionData.ageInYears)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`month`](#DateExpressionData.month)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`year`](#DateExpressionData.year)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`issuedDate`](#PaymentSourceInfoExpressionData.issuedDate).[`timestamp`](#DateExpressionData.timestamp)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`institutionName`](#PaymentSourceInfoExpressionData.institutionName)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`accountIdentifier`](#PaymentSourceInfoExpressionData.accountIdentifier)
- [`action`](#WorkflowExpressionContext.action).[`paymentSource`](#ApplicantActionExpressionData.paymentSource).[`fixedInfo`](#PaymentSourceExpressionData.fixedInfo).[`type`](#PaymentSourceInfoExpressionData.type)
- [`action`](#WorkflowExpressionContext.action).[`review`](#ApplicantActionExpressionData.review).[`buttonIds`](#InspectionReviewExpressionData.buttonIds)
- [`action`](#WorkflowExpressionContext.action).[`review`](#ApplicantActionExpressionData.review).[`rejectLabels`](#InspectionReviewExpressionData.rejectLabels)
- [`action`](#WorkflowExpressionContext.action).[`review`](#ApplicantActionExpressionData.review).[`attemptCnt`](#InspectionReviewExpressionData.attemptCnt)
- [`action`](#WorkflowExpressionContext.action).[`review`](#ApplicantActionExpressionData.review).[`levelName`](#InspectionReviewExpressionData.levelName)
- [`action`](#WorkflowExpressionContext.action).[`createdAt`](#ApplicantActionExpressionData.createdAt).[`ageInDays`](#DateExpressionData.ageInDays)
- [`action`](#WorkflowExpressionContext.action).[`createdAt`](#ApplicantActionExpressionData.createdAt).[`ageInYears`](#DateExpressionData.ageInYears)
- [`action`](#WorkflowExpressionContext.action).[`createdAt`](#ApplicantActionExpressionData.createdAt).[`dayOfMonth`](#DateExpressionData.dayOfMonth)
- [`action`](#WorkflowExpressionContext.action).[`createdAt`](#ApplicantActionExpressionData.createdAt).[`month`](#DateExpressionData.month)
- [`action`](#WorkflowExpressionContext.action).[`createdAt`](#ApplicantActionExpressionData.createdAt).[`year`](#DateExpressionData.year)
- [`action`](#WorkflowExpressionContext.action).[`createdAt`](#ApplicantActionExpressionData.createdAt).[`yyyymmdd`](#DateExpressionData.yyyymmdd)
- [`action`](#WorkflowExpressionContext.action).[`createdAt`](#ApplicantActionExpressionData.createdAt).[`timestamp`](#DateExpressionData.timestamp)
- [`action`](#WorkflowExpressionContext.action).[`externalActionId`](#ApplicantActionExpressionData.externalActionId)
- [`action`](#WorkflowExpressionContext.action).[`id`](#ApplicantActionExpressionData.id)
- [`random`](#WorkflowExpressionContext.random)

