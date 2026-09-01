## Types

### <a name="AmlRuleExpressionContext"></a>`Root variables`

| Field | Type | Description |
| --- | --- | --- |
| <a name="AmlRuleExpressionContext.applicant"></a>`applicant` | `Object` | Applicant information |
| <a name="AmlRuleExpressionContext.applicantIdDoc"></a>`applicantIdDoc` | `Object` |  |
| <a name="AmlRuleExpressionContext.input"></a>`input` | [`Object`](#ScreeningInputExpressionData) | Aml case input information |
| <a name="AmlRuleExpressionContext.screening"></a>`screening` | [`Object`](#AmlCaseExpressionData) | Aml case information |
| <a name="AmlRuleExpressionContext.match"></a>`match` | [`Object`](#HitExpressionData) | Current hit information |

### <a name="ScreeningInputExpressionData"></a>`input`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ScreeningInputExpressionData.firstName"></a>`firstName` | `String` | First name |
| <a name="ScreeningInputExpressionData.firstNameEn"></a>`firstNameEn` | `String` | Transliterated first name |
| <a name="ScreeningInputExpressionData.lastName"></a>`lastName` | `String` | Last name |
| <a name="ScreeningInputExpressionData.lastNameEn"></a>`lastNameEn` | `String` | Transliterated last name |
| <a name="ScreeningInputExpressionData.middleName"></a>`middleName` | `String` | Middle name |
| <a name="ScreeningInputExpressionData.middleNameEn"></a>`middleNameEn` | `String` | Transliterated middle name |
| <a name="ScreeningInputExpressionData.fullName"></a>`fullName` | `String` | Full name |
| <a name="ScreeningInputExpressionData.aliasName"></a>`aliasName` | `String` | Alias of the screened entity. For French passports, it's the value of the "epouse" field. |
| <a name="ScreeningInputExpressionData.gender"></a>`gender` | `String` | Gender (M or F) |
| <a name="ScreeningInputExpressionData.dob"></a>`dob` | `Date` | Date of birth |
| <a name="ScreeningInputExpressionData.country"></a>`country` | `String` | Country (ISO 3166-1 alpha-3) |
| <a name="ScreeningInputExpressionData.town"></a>`town` | `String` | Town if applicable. |
| <a name="ScreeningInputExpressionData.state"></a>`state` | `String` | State name or region if applicable. |
| <a name="ScreeningInputExpressionData.companyInfo"></a>`companyInfo` | [`Object`](#CompanyInputExpressionData) | Company information |
| <a name="ScreeningInputExpressionData.countries"></a>`countries` | List of `String`-s | Countries (ISO 3166-1 alpha-3) |
| <a name="ScreeningInputExpressionData.entityType"></a>`entityType` | `String` | input entity type: individual or company |
| <a name="ScreeningInputExpressionData.countryOfBirth"></a>`countryOfBirth` | `String` | Country of birth (ISO 3166-1 alpha-3) |
| <a name="ScreeningInputExpressionData.nationality"></a>`nationality` | `String` | Nationality (ISO 3166-1 alpha-3) |
| <a name="ScreeningInputExpressionData.analysis"></a>`analysis` | [`Object`](#ScreeningInputAnalysisExpressionData) | Some signals based on applicant input data |

### <a name="AmlCaseExpressionData"></a>`screening`

| Field | Type | Description |
| --- | --- | --- |
| <a name="AmlCaseExpressionData.id"></a>`id` | `String` | Aml case ID |
| <a name="AmlCaseExpressionData.createdAt"></a>`createdAt` | `Date` | Aml case creation date |
| <a name="AmlCaseExpressionData.targetEntityType"></a>`targetEntityType` | [`Enum`](#TargetEntityType) | Target entity type: applicant or transactionParticipant |
| <a name="AmlCaseExpressionData.vendor"></a>`vendor` | [`Enum`](#VendorType) | Aml screening vendor: ComplyAdvantage, etc. |
| <a name="AmlCaseExpressionData.hitsCount"></a>`hitsCount` | `int` | Matches count |
| <a name="AmlCaseExpressionData.riskLabels"></a>`riskLabels` | List of `String`-s | Risk labels collected from all matches in case |
| <a name="AmlCaseExpressionData.matchStatuses"></a>`matchStatuses` | List of `String`-s | Matches match statuses collected from all matches in case |
| <a name="AmlCaseExpressionData.answer"></a>`answer` | `String` | The GREEN/YELLOW/RED/ERROR answer of this check. |
| <a name="AmlCaseExpressionData.tags"></a>`tags` | List of `String`-s | AML case tags. One AML rule can add tag, another rule can use it in its condition. All AML tags stored in AML case. |

### <a name="HitExpressionData"></a>`match`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitExpressionData.name"></a>`name` | `String` | Match name |
| <a name="HitExpressionData.alternativeNames"></a>`alternativeNames` | List of `String`-s | Match alternative names |
| <a name="HitExpressionData.dobs"></a>`dobs` | [`Object`](#HitDobsExpressionData) | Match list of DoB: may be full DoB, may be only year of birth |
| <a name="HitExpressionData.gender"></a>`gender` | `String` | Gender of the matched entity. Null if not available or ambiguous. |
| <a name="HitExpressionData.riskLabels"></a>`riskLabels` | List of `String`-s | Aml case risk labels |
| <a name="HitExpressionData.previousReview"></a>`previousReview` | [`Object`](#HitReviewExpressionData) |  |
| <a name="HitExpressionData.complyAdvantage"></a>`complyAdvantage` | [`Object`](#HitComplyAdvantageInfoExpressionData) | ComplyAdvantage-specific match information. |
| <a name="HitExpressionData.complyAdvantageMesh"></a>`complyAdvantageMesh` | [`Object`](#HitComplyAdvantageMeshInfoExpressionData) | ComplyAdvantage-specific match information. |
| <a name="HitExpressionData.worldCheckOne"></a>`worldCheckOne` | [`Object`](#HitWorldCheckInfoExpressionData) | World Check One -specific match information. |
| <a name="HitExpressionData.quantifind"></a>`quantifind` | [`Object`](#HitQuantifindInfoExpressionData) | Quantifind-specific match information. |
| <a name="HitExpressionData.analysis"></a>`analysis` | [`Object`](#HitAnalysisExpressionData) | Some signals based on match data |
| <a name="HitExpressionData.sources"></a>`sources` | [`Object`](#HitSourcesExpressionData) | Some signals based on match sources |
| <a name="HitExpressionData.countries"></a>`countries` | [`Object`](#HitCountriesExpressionData) | Countries related to this match |

### <a name="CompanyInputExpressionData"></a>`input.companyInfo`

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyInputExpressionData.name"></a>`name` | `String` | Company name |
| <a name="CompanyInputExpressionData.alternativeNames"></a>`alternativeNames` | List of `String`-s | Alternative names |

### <a name="ScreeningInputAnalysisExpressionData"></a>`input.analysis`

| Field | Type | Description |
| --- | --- | --- |
| <a name="ScreeningInputAnalysisExpressionData.parentName"></a>`parentName` | `String` | Parent name extracted from input data |
| <a name="ScreeningInputAnalysisExpressionData.namesCount"></a>`namesCount` | `int` | Words count or hieroglyphs count in case applicant's name consist of hieroglyphs |

### <a name="TargetEntityType"></a>`screening.targetEntityType`

TargetEntityType specifies type of screened entity: applicant or transaction participant

| Value | Description |
| --- | --- |
| `applicant` |  |
| `transactionParticipant` |  |

### <a name="VendorType"></a>`screening.vendor`

| Value | Description |
| --- | --- |
| `complyAdvantageCSOM` | Comply Advantage CSOM AML vendor |
| `worldCheckOne` | World Check One AML vendor |
| `quantifind` | Quantifind Graphyte AML vendor |
| `complyAdvantageMesh` | Comply Advantage Mesh AML vendor |

### <a name="HitDobsExpressionData"></a>`match.dobs`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitDobsExpressionData.hasData"></a>`hasData` | `boolean` |  |

### <a name="HitReviewExpressionData"></a>`match.previousReview`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitReviewExpressionData.matchStatus"></a>`matchStatus` | `String` |  |
| <a name="HitReviewExpressionData.riskLevel"></a>`riskLevel` | `String` |  |
| <a name="HitReviewExpressionData.whitelisted"></a>`whitelisted` | `Boolean` |  |
| <a name="HitReviewExpressionData.modifiedAt"></a>`modifiedAt` | `Date` | Date of last review modification. |
| <a name="HitReviewExpressionData.note"></a>`note` | `String` | Freeform note left by a reviewer. |

### <a name="HitComplyAdvantageInfoExpressionData"></a>`match.complyAdvantage`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitComplyAdvantageInfoExpressionData.warningTypes"></a>`warningTypes` | List of `String`-s | Types like 'pep', 'sanctions', etc - vendor specific |
| <a name="HitComplyAdvantageInfoExpressionData.matchTypes"></a>`matchTypes` | List of `String`-s | Match type looks like 'name_exact' or 'aka_fuzzy'; allowed values in [aml-rules-enumerations.md](aml-rules-enumerations.md#MatchType). |

### <a name="HitComplyAdvantageMeshInfoExpressionData"></a>`match.complyAdvantageMesh`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitComplyAdvantageMeshInfoExpressionData.warningTypes"></a>`warningTypes` | List of `String`-s | Types like 'pep', 'sanctions', etc - vendor specific |
| <a name="HitComplyAdvantageMeshInfoExpressionData.matchTypes"></a>`matchTypes` | List of `String`-s | Match type looks like 'name_exact' or 'aka_fuzzy'; allowed values in [aml-rules-enumerations.md](aml-rules-enumerations.md#MatchType). |

### <a name="HitWorldCheckInfoExpressionData"></a>`match.worldCheckOne`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitWorldCheckInfoExpressionData.warningTypes"></a>`warningTypes` | List of `String`-s | Types like 'pep', 'sanctions', etc - vendor specific |
| <a name="HitWorldCheckInfoExpressionData.resolutionDate"></a>`resolutionDate` | `Date` | Date hit was resolved on WC1's side |
| <a name="HitWorldCheckInfoExpressionData.matchStatus"></a>`matchStatus` | `String` | Match status based on resolution toolkit |
| <a name="HitWorldCheckInfoExpressionData.riskLevel"></a>`riskLevel` | `String` | Risk level based on resolution toolkit |

### <a name="HitQuantifindInfoExpressionData"></a>`match.quantifind`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitQuantifindInfoExpressionData.riskLevel"></a>`riskLevel` | `String` | Risk level. |
| <a name="HitQuantifindInfoExpressionData.confidence"></a>`confidence` | `String` | Quantifind assessed Confidence Level of the match; values of “Strong”, “Fair”, Weak” |

### <a name="HitAnalysisExpressionData"></a>`match.analysis`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitAnalysisExpressionData.parentName"></a>`parentName` | `String` | Parent name extracted from match data |
| <a name="HitAnalysisExpressionData.tinCompatible"></a>`tinCompatible` | `Boolean` | true if national id or TIN of the applicant matches nationalId/TIN of the match |
| <a name="HitAnalysisExpressionData.namesCount"></a>`namesCount` | `int` | Words count or hieroglyphs count in case applicant's name consist of hieroglyphs |
| <a name="HitAnalysisExpressionData.pep"></a>`pep` | [`Object`](#PepAnalysisExpressionData) | Politically exposed person's match data analysis |
| <a name="HitAnalysisExpressionData.company"></a>`company` | [`Object`](#CompanyAnalysisExpressionData) | Company match data analysis (computed only when the screened entity is a company) |

### <a name="HitSourcesExpressionData"></a>`match.sources`

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitSourcesExpressionData.earliestStartDate"></a>`earliestStartDate` | `Date` | Null if all source's startDate is null, otherwise the min(startDates). |
| <a name="HitSourcesExpressionData.latestEndDate"></a>`latestEndDate` | `Date` | Null if all source's endDate is null, otherwise the max(endDates) |

### <a name="HitCountriesExpressionData"></a>`match.countries`

Holds ISO 3166-1 alpha-3 country codes extracted from a watchlist hit, grouped by the role
 each country plays for the sanctioned entity. Used as an expression context variable in AML rules.

| Field | Type | Description |
| --- | --- | --- |
| <a name="HitCountriesExpressionData.all"></a>`all` | List of `String`-s | Deduplicated union of all country codes across every role. |
| <a name="HitCountriesExpressionData.location"></a>`location` | List of `String`-s | Countries associated with the entity's physical location. |
| <a name="HitCountriesExpressionData.placeOfBirth"></a>`placeOfBirth` | List of `String`-s | Countries associated with the entity's place of birth. |
| <a name="HitCountriesExpressionData.placeOfDeath"></a>`placeOfDeath` | List of `String`-s | Countries associated with the entity's place of death. |
| <a name="HitCountriesExpressionData.operatesIn"></a>`operatesIn` | List of `String`-s | Countries in which the entity operates. |
| <a name="HitCountriesExpressionData.registeredIn"></a>`registeredIn` | List of `String`-s | Countries in which the entity is registered. |
| <a name="HitCountriesExpressionData.vesselFlag"></a>`vesselFlag` | List of `String`-s | Flag countries for vessels associated with the entity. |

### <a name="PepAnalysisExpressionData"></a>`match.analysis.pep`

| Field | Type | Description |
| --- | --- | --- |
| <a name="PepAnalysisExpressionData.institutionKinds"></a>`institutionKinds` | List of `String`-s | Kinds of political institutions encountered in the match data. |
| <a name="PepAnalysisExpressionData.institutionJurisdictions"></a>`institutionJurisdictions` | List of `String`-s | Jurisdiction types of political institutions encountered in the match data. |
| <a name="PepAnalysisExpressionData.institutionRegionVsInputComparisons"></a>`institutionRegionVsInputComparisons` | List of `String`-s | Comparisons between screened person's address and the regions associated with political institutions present in the match data. |
| <a name="PepAnalysisExpressionData.declassificationDate"></a>`declassificationDate` | `Date` | Date when, according to the match data, either the person vacated the political position or this position stopped to be recognized as political due to a regulatory change. <br> When multiple positions: - If any doesn't specify an end date, declassificationDate is none. - If all specify an end date, declassificationDate is the most recent one. |
| <a name="PepAnalysisExpressionData.associationEndDate"></a>`associationEndDate` | `Date` | Date when, according to the match data, the association between the person and a PEP ceased. |

### <a name="CompanyAnalysisExpressionData"></a>`match.analysis.company`

Company-specific match analysis exposed to AML rules as `match.analysis.company`.
 Currently carries only `nameCompatibility` — how well the screened company name resembles
 the watchlist-hit name (country- and legal-form-aware), used to suppress false positives.

| Field | Type | Description |
| --- | --- | --- |
| <a name="CompanyAnalysisExpressionData.nameCompatibility"></a>`nameCompatibility` | `String` | Strongest name-compatibility confidence level across every screened-name vs hit-name pair (high > medium > low > negligible. notApplicable result means one of the input names is either empty or written in an unsupported script. |

## Index

- [`applicant`](#AmlRuleExpressionContext.applicant)
- [`applicantIdDoc`](#AmlRuleExpressionContext.applicantIdDoc)
- [`input`](#AmlRuleExpressionContext.input).[`analysis`](#ScreeningInputExpressionData.analysis).[`namesCount`](#ScreeningInputAnalysisExpressionData.namesCount)
- [`input`](#AmlRuleExpressionContext.input).[`analysis`](#ScreeningInputExpressionData.analysis).[`parentName`](#ScreeningInputAnalysisExpressionData.parentName)
- [`input`](#AmlRuleExpressionContext.input).[`nationality`](#ScreeningInputExpressionData.nationality)
- [`input`](#AmlRuleExpressionContext.input).[`countryOfBirth`](#ScreeningInputExpressionData.countryOfBirth)
- [`input`](#AmlRuleExpressionContext.input).[`entityType`](#ScreeningInputExpressionData.entityType)
- [`input`](#AmlRuleExpressionContext.input).[`countries`](#ScreeningInputExpressionData.countries)
- [`input`](#AmlRuleExpressionContext.input).[`companyInfo`](#ScreeningInputExpressionData.companyInfo).[`alternativeNames`](#CompanyInputExpressionData.alternativeNames)
- [`input`](#AmlRuleExpressionContext.input).[`companyInfo`](#ScreeningInputExpressionData.companyInfo).[`name`](#CompanyInputExpressionData.name)
- [`input`](#AmlRuleExpressionContext.input).[`state`](#ScreeningInputExpressionData.state)
- [`input`](#AmlRuleExpressionContext.input).[`town`](#ScreeningInputExpressionData.town)
- [`input`](#AmlRuleExpressionContext.input).[`country`](#ScreeningInputExpressionData.country)
- [`input`](#AmlRuleExpressionContext.input).[`dob`](#ScreeningInputExpressionData.dob)
- [`input`](#AmlRuleExpressionContext.input).[`gender`](#ScreeningInputExpressionData.gender)
- [`input`](#AmlRuleExpressionContext.input).[`aliasName`](#ScreeningInputExpressionData.aliasName)
- [`input`](#AmlRuleExpressionContext.input).[`fullName`](#ScreeningInputExpressionData.fullName)
- [`input`](#AmlRuleExpressionContext.input).[`middleNameEn`](#ScreeningInputExpressionData.middleNameEn)
- [`input`](#AmlRuleExpressionContext.input).[`middleName`](#ScreeningInputExpressionData.middleName)
- [`input`](#AmlRuleExpressionContext.input).[`lastNameEn`](#ScreeningInputExpressionData.lastNameEn)
- [`input`](#AmlRuleExpressionContext.input).[`lastName`](#ScreeningInputExpressionData.lastName)
- [`input`](#AmlRuleExpressionContext.input).[`firstNameEn`](#ScreeningInputExpressionData.firstNameEn)
- [`input`](#AmlRuleExpressionContext.input).[`firstName`](#ScreeningInputExpressionData.firstName)
- [`screening`](#AmlRuleExpressionContext.screening).[`tags`](#AmlCaseExpressionData.tags)
- [`screening`](#AmlRuleExpressionContext.screening).[`answer`](#AmlCaseExpressionData.answer)
- [`screening`](#AmlRuleExpressionContext.screening).[`matchStatuses`](#AmlCaseExpressionData.matchStatuses)
- [`screening`](#AmlRuleExpressionContext.screening).[`riskLabels`](#AmlCaseExpressionData.riskLabels)
- [`screening`](#AmlRuleExpressionContext.screening).[`hitsCount`](#AmlCaseExpressionData.hitsCount)
- [`screening`](#AmlRuleExpressionContext.screening).[`vendor`](#AmlCaseExpressionData.vendor)
- [`screening`](#AmlRuleExpressionContext.screening).[`targetEntityType`](#AmlCaseExpressionData.targetEntityType)
- [`screening`](#AmlRuleExpressionContext.screening).[`createdAt`](#AmlCaseExpressionData.createdAt)
- [`screening`](#AmlRuleExpressionContext.screening).[`id`](#AmlCaseExpressionData.id)
- [`match`](#AmlRuleExpressionContext.match).[`countries`](#HitExpressionData.countries).[`vesselFlag`](#HitCountriesExpressionData.vesselFlag)
- [`match`](#AmlRuleExpressionContext.match).[`countries`](#HitExpressionData.countries).[`registeredIn`](#HitCountriesExpressionData.registeredIn)
- [`match`](#AmlRuleExpressionContext.match).[`countries`](#HitExpressionData.countries).[`operatesIn`](#HitCountriesExpressionData.operatesIn)
- [`match`](#AmlRuleExpressionContext.match).[`countries`](#HitExpressionData.countries).[`placeOfDeath`](#HitCountriesExpressionData.placeOfDeath)
- [`match`](#AmlRuleExpressionContext.match).[`countries`](#HitExpressionData.countries).[`placeOfBirth`](#HitCountriesExpressionData.placeOfBirth)
- [`match`](#AmlRuleExpressionContext.match).[`countries`](#HitExpressionData.countries).[`location`](#HitCountriesExpressionData.location)
- [`match`](#AmlRuleExpressionContext.match).[`countries`](#HitExpressionData.countries).[`all`](#HitCountriesExpressionData.all)
- [`match`](#AmlRuleExpressionContext.match).[`sources`](#HitExpressionData.sources).[`latestEndDate`](#HitSourcesExpressionData.latestEndDate)
- [`match`](#AmlRuleExpressionContext.match).[`sources`](#HitExpressionData.sources).[`earliestStartDate`](#HitSourcesExpressionData.earliestStartDate)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`company`](#HitAnalysisExpressionData.company).[`nameCompatibility`](#CompanyAnalysisExpressionData.nameCompatibility)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`pep`](#HitAnalysisExpressionData.pep).[`associationEndDate`](#PepAnalysisExpressionData.associationEndDate)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`pep`](#HitAnalysisExpressionData.pep).[`declassificationDate`](#PepAnalysisExpressionData.declassificationDate)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`pep`](#HitAnalysisExpressionData.pep).[`institutionRegionVsInputComparisons`](#PepAnalysisExpressionData.institutionRegionVsInputComparisons)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`pep`](#HitAnalysisExpressionData.pep).[`institutionJurisdictions`](#PepAnalysisExpressionData.institutionJurisdictions)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`pep`](#HitAnalysisExpressionData.pep).[`institutionKinds`](#PepAnalysisExpressionData.institutionKinds)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`namesCount`](#HitAnalysisExpressionData.namesCount)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`tinCompatible`](#HitAnalysisExpressionData.tinCompatible)
- [`match`](#AmlRuleExpressionContext.match).[`analysis`](#HitExpressionData.analysis).[`parentName`](#HitAnalysisExpressionData.parentName)
- [`match`](#AmlRuleExpressionContext.match).[`quantifind`](#HitExpressionData.quantifind).[`confidence`](#HitQuantifindInfoExpressionData.confidence)
- [`match`](#AmlRuleExpressionContext.match).[`quantifind`](#HitExpressionData.quantifind).[`riskLevel`](#HitQuantifindInfoExpressionData.riskLevel)
- [`match`](#AmlRuleExpressionContext.match).[`worldCheckOne`](#HitExpressionData.worldCheckOne).[`riskLevel`](#HitWorldCheckInfoExpressionData.riskLevel)
- [`match`](#AmlRuleExpressionContext.match).[`worldCheckOne`](#HitExpressionData.worldCheckOne).[`matchStatus`](#HitWorldCheckInfoExpressionData.matchStatus)
- [`match`](#AmlRuleExpressionContext.match).[`worldCheckOne`](#HitExpressionData.worldCheckOne).[`resolutionDate`](#HitWorldCheckInfoExpressionData.resolutionDate)
- [`match`](#AmlRuleExpressionContext.match).[`worldCheckOne`](#HitExpressionData.worldCheckOne).[`warningTypes`](#HitWorldCheckInfoExpressionData.warningTypes)
- [`match`](#AmlRuleExpressionContext.match).[`complyAdvantageMesh`](#HitExpressionData.complyAdvantageMesh).[`matchTypes`](#HitComplyAdvantageMeshInfoExpressionData.matchTypes)
- [`match`](#AmlRuleExpressionContext.match).[`complyAdvantageMesh`](#HitExpressionData.complyAdvantageMesh).[`warningTypes`](#HitComplyAdvantageMeshInfoExpressionData.warningTypes)
- [`match`](#AmlRuleExpressionContext.match).[`complyAdvantage`](#HitExpressionData.complyAdvantage).[`matchTypes`](#HitComplyAdvantageInfoExpressionData.matchTypes)
- [`match`](#AmlRuleExpressionContext.match).[`complyAdvantage`](#HitExpressionData.complyAdvantage).[`warningTypes`](#HitComplyAdvantageInfoExpressionData.warningTypes)
- [`match`](#AmlRuleExpressionContext.match).[`previousReview`](#HitExpressionData.previousReview).[`note`](#HitReviewExpressionData.note)
- [`match`](#AmlRuleExpressionContext.match).[`previousReview`](#HitExpressionData.previousReview).[`modifiedAt`](#HitReviewExpressionData.modifiedAt)
- [`match`](#AmlRuleExpressionContext.match).[`previousReview`](#HitExpressionData.previousReview).[`whitelisted`](#HitReviewExpressionData.whitelisted)
- [`match`](#AmlRuleExpressionContext.match).[`previousReview`](#HitExpressionData.previousReview).[`riskLevel`](#HitReviewExpressionData.riskLevel)
- [`match`](#AmlRuleExpressionContext.match).[`previousReview`](#HitExpressionData.previousReview).[`matchStatus`](#HitReviewExpressionData.matchStatus)
- [`match`](#AmlRuleExpressionContext.match).[`riskLabels`](#HitExpressionData.riskLabels)
- [`match`](#AmlRuleExpressionContext.match).[`gender`](#HitExpressionData.gender)
- [`match`](#AmlRuleExpressionContext.match).[`dobs`](#HitExpressionData.dobs).[`hasData`](#HitDobsExpressionData.hasData)
- [`match`](#AmlRuleExpressionContext.match).[`alternativeNames`](#HitExpressionData.alternativeNames)
- [`match`](#AmlRuleExpressionContext.match).[`name`](#HitExpressionData.name)

## Functions

| Function | Return type | Description |
| --- | --- | --- |
| ``namesCompatible(HitExpressionData match, String name, String country, String comparisonMode, Boolean compareAlternativeNames)`` | boolean | Returns <code>true</code>true - if match name equals to the specified name Calculates if match name and the specified name are compatible. The specified country and settings are used to compare names.<br/> Parameters: <ul><li>``HitExpressionData match`` - - the match data to compare</li><li>``String name`` - - the name to compare with</li><li>``String country`` - - the specified country's normalization rules are used comparing names</li><li>``String comparisonMode`` - - Name comparison mode: strict or weakContainment.</li><li>``Boolean compareAlternativeNames`` - - Flag indicating if alternative names of the match will be taken into account.</li></ul> |
| ``namesIncompatible(HitExpressionData match, String name, String country, String comparisonMode, Boolean compareAlternativeNames)`` | boolean | Returns <code>true</code>true - if match name equals to the specified name Calculates if match name and the specified name are NOT compatible. The specified country and settings are used to compare names.<br/> Parameters: <ul><li>``HitExpressionData match`` - - the match data to compare</li><li>``String name`` - - the name to compare with</li><li>``String country`` - - the specified country's normalization rules are used comparing names</li><li>``String comparisonMode`` - - Name comparison mode: strict or weakContainment.</li><li>``Boolean compareAlternativeNames`` - - Flag indicating if alternative names of the match will be taken into account.</li></ul> |
| ``dobsCompatible(HitDobsExpressionData dobs, DateExpressionData date, String comparisonMode)`` | boolean | Returns <code>true</code>true - if match any dates of birth equals to the specified name Calculates if match any dates of birth and the specified date are compatible. The specified country and settings are used to compare names.<br/> Parameters: <ul><li>``HitDobsExpressionData dobs`` - - the match dates of birth</li><li>``DateExpressionData date`` - - the date to compare with</li><li>``String comparisonMode`` - - Dob comparison mode: strict or weakContainment.</li></ul> |
| ``dobsIncompatible(HitDobsExpressionData dobs, DateExpressionData date, String comparisonMode)`` | boolean | Returns <code>true</code>true - if match any dates of birth equals to the specified name Calculates if match any dates of birth and the specified date are NOT compatible. The specified country and settings are used to compare names.<br/> Parameters: <ul><li>``HitDobsExpressionData dobs`` - - the match dates of birth</li><li>``DateExpressionData date`` - - the date to compare with</li><li>``String comparisonMode`` - - Dob comparison mode: strict or weakContainment.</li></ul> |