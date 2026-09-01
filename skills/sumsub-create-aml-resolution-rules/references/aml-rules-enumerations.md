# AML resolution rules — enumerations reference

Allowed values for the AML rule-context fields that are **closed enums** — fields that show as plain `String` / `List of String` 
in [`aml-rules-context-fields.md`](aml-rules-context-fields.md) but only ever hold one of a fixed set of values. 
Check here for the valid values (and what they mean) before comparing against such a field. A few entries have 
no description yet — the value itself is still authoritative.

> A field typed `List of String` here carries a **subset** of these values. To match "only value X" use `containsOnly ["X"]` (never `notContainsAny [the-others]` — see the operator note in [`aml-resolution-rules-schema.md`](aml-resolution-rules-schema.md)).

### <a name="InputEntityType"></a>`InputEntityType`

Used by: `input.entityType`

| Value        | Description                                                                                        |
|--------------|----------------------------------------------------------------------------------------------------|
| `unknown`    | The screening input's entity type is unknown at the time of the screening.                         |
| `individual` | Screened entity is an individual.                                                                  |
| `company`    | Screened entity is a legal entity, such as a company, corporation, organization or an institution. |

### <a name="CompanyNameConfidenceLevel"></a>`CompanyNameConfidenceLevel`

Used by: `match.analysis.company.nameCompatibility`

| Value           | Description                                                                                                                                               |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `high`          | names very likely the same organization                                                                                                                   |
| `medium`        | important differences but cannot be ruled out: e.g. a clearly different legal form, or one side adds only common/low-significance tokens to a shared core |
| `low`           | a significant token matches but each side has its own distinct significant tokens (a remote partial match)                                                |
| `negligible`    | no significant shared token; almost zero chance of the same org                                                                                           |
| `notApplicable` | nothing comparable: blank/placeholder, every token stripped as a legal form, or a script we cannot read.                                                  |

### <a name="InstitutionJurisdiction"></a>`InstitutionJurisdiction`

Used by: `match.analysis.pep.institutionJurisdictions`

| Value              | Description                                                                                                                                                                                            |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `international`    | Jurisdiction spans multiple sovereign states; the institution is not part of any single national government (e.g. UN, EU institutions, IMF, World Bank, African Union, ICC).                           |
| `national`         | Country-wide / sovereign-state level. In federations this includes the federal government.                                                                                                             |
| `subnational`      | First-level country subdivision with its own elected or appointed government — state, province, region, oblast, prefecture, federative unit, autonomous community, krai, voivodeship, federal subject. |
| `local`            | Sub-state or municipal level — county, district, city, town, commune, municipality, borough, parish, raion.                                                                                            |
| `extraterritorial` | Institution belongs to country A but is physically seated and operates in country B. Typically used for diplomatic missions abroad and military bases abroad.                                          |
| `unknown`          | Jurisdiction cannot be determined from the provided sources.                                                                                                                                           |

### <a name="InstitutionKind"></a>`InstitutionKind`

Used by: `match.analysis.pep.institutionKinds`

| Value                       | Description                                                                                                                                                                                                                  |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `legislature`               | Law-making body at any territorial level — national parliament or congress, regional or state legislature, city or county council with legislative power.                                                                    |
| `executiveBody`             | Any executive-branch body regardless of seniority — head of state or government office, cabinet, regional or local executive, ministry, department, executive agency, or public agency that is not an independent regulator. |
| `regulatoryAgency`          | Independent regulator with statutory authority — election commission, anti-corruption agency, competition / financial / data-protection regulator.                                                                           |
| `court`                     | Judicial body — constitutional, supreme, appellate, federal, regional, local, specialised tribunal, or military court.                                                                                                       |
| `prosecutorOffice`          | Public prosecution authority, procuracy, or attorney general's office.                                                                                                                                                       |
| `auditInstitution`          | Supreme audit body, court of accounts, or national audit office.                                                                                                                                                             |
| `lawEnforcement`            | Police, gendarmerie, or other uniformed service with a policing function (non-military).                                                                                                                                     |
| `armedForces`               | Military body — army, navy, air force, joint command, or branch of the armed forces.                                                                                                                                         |
| `intelligenceAgency`        | Civilian or military intelligence or security service.                                                                                                                                                                       |
| `diplomaticMission`         | Embassy, consulate, permanent mission to an international organisation, or ambassador-at-large posting.                                                                                                                      |
| `internationalOrganization` | Inter-governmental organisation and its organs (UN, EU, IMF, World Bank, African Union, OAS, ASEAN, etc.).                                                                                                                   |
| `centralBank`               | Central or reserve bank, or other monetary authority.                                                                                                                                                                        |
| `stateOwnedEnterprise`      | Corporate entity owned or controlled by the state at any level. Includes boards of state-controlled companies.                                                                                                               |
| `politicalParty`            | Political party leadership organ or parliamentary party. In one-party systems, the party's executive committee.                                                                                                              |
| `monarchy`                  | Reigning royal house — monarchs, regents, or royal family members acting in a head-of-state capacity.                                                                                                                        |
| `religiousAuthority`        | Head or senior office-holder of a state-recognised religious institution where religion has a constitutional role.                                                                                                           |
| `electoralBody`             | Election commission, electoral tribunal, or supreme electoral court.                                                                                                                                                         |
| `other`                     | The institution does not fit any specific kind above, or the role description is too generic to classify (e.g. 'Senior Government Official' or 'Politician' without further context).                                        |

### <a name="InstitutionRegionVsInputComparison"></a>`InstitutionRegionVsInputComparison`

Used by: `match.analysis.pep.institutionRegionVsInputComparisons`

| Value                              | Description                                                                                                                                                                                             |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `same`                             | Same country and same first-level subdivision between the screened person's address and the institution's region.                                                                                       |
| `differentRegionWithinSameCountry` | Same country, but different first-level subdivision. Both regions must be independently identified in the data for this verdict.                                                                        |
| `differentCountry`                 | The screened person's address and the institution are in different countries.                                                                                                                           |
| `indeterminable`                   | The comparison cannot be made — either side lacks a clearly identified first-level subdivision, the institution operates across multiple countries, or the regional signals in the match data conflict. |

### <a name="MatchType"></a>`MatchType`

Used by: `match.complyAdvantage.matchTypes`, `match.complyAdvantageMesh.matchTypes`

| Value                     | Description                                                                           |
|---------------------------|---------------------------------------------------------------------------------------|
| `unknown`                 | Matched for a more complex reason, such as based on an acronym.                       |
| `name_exact`              | Matched against the entity name exactly.                                              |
| `name_compatible`         |                                                                                       |
| `equivalent_name`         | Matched against the entity name with a synonym, e.g. 'Robert Mugabe' => 'Bob Mugabe'. |
| `name_synonym`            |                                                                                       |
| `aka_exact`               | Matched against an entity AKA (also known as) entry exactly.                          |
| `aka_synonym`             |                                                                                       |
| `aka_phonetic`            |                                                                                       |
| `fuzzy`                   |                                                                                       |
| `name_fuzzy`              | Matched closely to the name, but at least one word had an edit-distance change.       |
| `dob_exact`               |                                                                                       |
| `year_of_birth`           | Matched the birth year as given in filters; can be the exact year or ±1 year.         |
| `year_and_month_of_birth` |                                                                                       |
| `address_exact`           |                                                                                       |
| `address_partial`         |                                                                                       |
| `phonetic_name`           | Matched against the entity name phonetically.                                         |
| `phonetic_aka`            | Matched against an entity AKA phonetically.                                           |
| `aka_fuzzy`               | Matched closely to an AKA name, but at least one word had an edit-distance change.    |
| `name_variations_removal` |                                                                                       |
| `removed_personal_suffix` | A personal suffix, for example 'PhD', was stripped from the search term.              |
| `removed_personal_title`  | A personal title, for example 'Mrs', was stripped from the search term.               |

### <a name="ConfidenceLevel"></a>`ConfidenceLevel`

Used by: `match.quantifind.confidence`

| Value    | Description                                                |
|----------|------------------------------------------------------------|
| `Strong` | Quantifind-assessed Confidence Level of the match: Strong. |
| `Fair`   | Quantifind-assessed Confidence Level of the match: Fair.   |
| `Weak`   | Quantifind-assessed Confidence Level of the match: Weak.   |

### <a name="QuantifindRiskLevel"></a>`QuantifindRiskLevel`

Used by: `match.quantifind.riskLevel`

| Value     | Description |
|-----------|-------------|
| `high`    | High        |
| `medium`  | Medium      |
| `neutral` | Neutral     |
| `noRisk`  | NoRisk      |

### <a name="ImageTestAnswer"></a>`ImageTestAnswer`

Used by: `screening.answer`

| Value     | Description                                                                      |
|-----------|----------------------------------------------------------------------------------|
| `IGNORED` | Check was skipped.                                                               |
| `GREEN`   | Everything is fine.                                                              |
| `YELLOW`  | Fine with some warnings / but most likely undefined (requires attention, review) |
| `RED`     | Some violations found.                                                           |
| `ERROR`   | Error occurred.                                                                  |

### <a name="WatchlistMatchStatus"></a>`WatchlistMatchStatus`

Used by: `screening.matchStatuses`, `match.previousReview.matchStatus`, `match.worldCheckOne.matchStatus`

| Value                     | Description                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `unknown`                 | There is no answer yet, the hit is still to be reviewed or the review is now irrelevant due to the presence of other reviewed matches. |
| `potential_match`         | AML hit (match) potentially identifies the same person as specified by the screening input.                                            |
| `false_positive`          | AML hit (match) is most likely identifying an entity that is different to one specified by the screening input.                        |
| `true_positive`           | AML hit (match) identifies the same person as specified by the screening input.                                                        |

### <a name="AmlRiskLabel"></a>`AmlRiskLabel`

Used by: `screening.riskLabels`, `match.riskLabels`

| Value            | Description                                                                                                                                                                                                           |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `pep`            | The screened entity belongs to the PEP (Politically Exposed Person) category.                                                                                                                                         |
| `sanctions`      | The screened entity was found in sanctions lists.                                                                                                                                                                     |
| `terrorism`      | The screened entity is suspected of terrorism.                                                                                                                                                                        |
| `crime`          | The screened entity is suspected of criminal activity.                                                                                                                                                                |
| `adverseMedia`   | The compromising published information that is related to the user was found in the media.                                                                                                                            |
| `fitnessProbity` | The screened entity does not comply with Fitness and Probity regime. The core function of the Fitness and Probity Regime is to ensure that individuals in key and customer facing positions are competent and capable |

### <a name="NameComparisonMode"></a>`NameComparisonMode`

Used by: the `comparisonMode` argument of the `namesCompatible` / `namesIncompatible` functions (`call`).

| Value             | Description |
|-------------------|-------------|
| `strict`          |             |
| `weakContainment` |             |
| `def`             |             |
| `ai`              |             |

### <a name="DobComparisonMode"></a>`DobComparisonMode`

Used by: the `comparisonMode` argument of the `dobsCompatible` / `dobsIncompatible` functions (`call`).

| Value             | Description |
|-------------------|-------------|
| `strict`          |             |
| `weakContainment` |             |
| `def`             |             |
