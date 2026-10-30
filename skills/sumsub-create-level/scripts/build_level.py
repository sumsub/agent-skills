#!/usr/bin/env python3
"""
Expand a compact level spec (JSON or YAML on stdin) into a full Sumsub
`ApplicantLevel` payload (JSON on stdout).

YAML support requires PyYAML (`pip install pyyaml`). If PyYAML is not
installed, only JSON input is accepted.

See SKILL.md for the spec format; this builder pads sensible defaults
per docSet type, validates enums, and passes unknown keys through.

`--base <file>` updates a company (KYB) level: the file holds the level's
GET response, and the output is that level with the spec laid over it.
PATCH replaces each nested object it gets (`requiredIdDocs`,
`autoCheckGeneratorSettings`) as a whole, so a body built from the spec
alone would drop every step and KYB setting the spec doesn't carry. It
refuses a copy of another account's level and WebSDK 1.0 levels.

`--levels <file>` (the level list) checks that every associated party's
levelName names an existing standalone level of the party's kind.

`--check` reads a built payload instead of a spec. For a company level it
refuses anything the builder wouldn't produce — post_level.sh and
patch_level.sh run it before every company-level write, so a payload the
builder rejected, or one written by hand, never reaches the API.
"""
import argparse
import copy
import json
import re
import sys

try:
    import yaml  # type: ignore
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def _load_spec(stream):
    """Parse stdin as YAML (which is a JSON superset) if PyYAML is available;
    otherwise fall back to JSON. On parse failure, surface a helpful error."""
    data = stream.read()
    if _HAS_YAML:
        try:
            return yaml.safe_load(data)
        except yaml.YAMLError as e:
            print(f"error: failed to parse spec as YAML/JSON: {e}", file=sys.stderr)
            sys.exit(2)
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        print(f"error: failed to parse spec as JSON: {e}", file=sys.stderr)
        print("hint: install PyYAML (`pip install pyyaml`) to accept YAML input.", file=sys.stderr)
        sys.exit(2)

SET_TYPES = {
    "APPLICANT_DATA", "EMAIL_VERIFICATION", "PHONE_VERIFICATION",
    "IDENTITY", "IDENTITY2", "IDENTITY3", "IDENTITY4",
    "SELFIE", "SELFIE2",
    "PROOF_OF_RESIDENCE", "PROOF_OF_RESIDENCE2",
    "PROOF_OF_PAYMENT", "PAYMENT_METHODS", "INVESTABILITY",
    "ACCREDITED_INVESTOR", "E_SIGN",
    "QUESTIONNAIRE", "QUESTIONNAIRE2", "QUESTIONNAIRE3", "QUESTIONNAIRE4",
    "E_KYC", "OTHER_DOCS", "COMPANY_DATA", "COMPANY_DOCUMENTS",
    "COMPANY_BENEFICIARIES", "TR_RECIPIENT_INFORMATION", "DEVICE_CHECK",
    "SOLANA_ATTESTATION", "LINEA_ATTESTATION", "CHAINLINK_ATTESTATION",
}
UNSUPPORTED_SET_TYPES = {
    "COMPANY": (
        "COMPANY is the legacy WebSDK 1.0 KYB step and the API rejects it on WebSDK 2.0 levels — "
        "build KYB levels from COMPANY_DATA, COMPANY_DOCUMENTS and COMPANY_BENEFICIARIES instead"
    ),
    "COMPANY_ADDRESSES": (
        "COMPANY_ADDRESSES is not supported by this skill yet — add company addresses in the Sumsub dashboard"
    ),
}
LEVEL_TYPES = {"standalone", "actions", "module"}
APPLICANT_TYPES = {"individual", "company"}
# ApplicantActionType in the API; only paymentMethod has extra checks below.
ACTION_TYPES = {"paymentMethod", "cryptoTransaction", "selfieAuth", "faceEnrollment"}
# IDENTITY: only `disabled` and `docapture` are actionable. Other VideoRequired
# values fall through to null in ApplicantHelper.getCaptureParams (verified).
IDENTITY_VIDEO_REQUIRED = {"disabled", "docapture"}
# SELFIE: all values the read-mapper handles, including non-public/deprecated
# (so GET→PATCH round-trip of legacy levels doesn't break).
SELFIE_VIDEO_REQUIRED = {"disabled", "enabled", "photoRequired", "passiveLiveness", "staticLiveness", "liveness", "optional"}
# captureMode includes deprecated `manualAfterTimeout` — backend doesn't reject it
# on write, and legacy levels may still carry it.
CAPTURE_MODES = {"manualAndAuto", "manualOnly", "seamless", "manualAfterTimeout"}
UPLOADER_MODES = {"always", "never", "fallback"}
NFC_MODES = {"disabled", "optional", "required"}
WALLET_SCREENING_PROVIDERS = {"crystal", "merkle", "trmLabs", "chainalysis", "elliptic", "cyvers"}
BANK_CARD_COUNT_IMAGES = {"one", "two", "some"}
UNHOSTED_WALLET_FORM_TYPES = {"DEFAULT", "SIMPLE", "KAZ", "TUR", "SGP", "POL", "ITA"}

# The per-level check flags inside fraudPreventionSettings. Each one is tri-state
# on the server: absent means "inherit the client-wide default", true/false pins
# it for this level. Unknown keys are silently dropped by the API, so validate
# them here.
FRAUD_PREVENTION_CHECKS = {
    "advancedEmailCheckEnabled",
    "advancedPhoneCheckEnabled",
    "advancedIpCheckEnabled",
    "advancedIdentityEnrichmentEnabled",
    "deviceIntelligenceEnabled",
}

# On update the spec leaves out what the user did not ask to change, so these
# fields come from `base` before the defaults and checks below read them.
BASE_INHERITED = ("type", "applicantType", "actionType", "websdkNext", "useCustomFraudPreventionSettings")
# Server-populated fields of the GET body, never sent back (references/level-schema.md).
SERVER_FIELDS = {"_id", "clientId", "key", "createdAt", "createdBy", "modifiedAt", "created", "modified"}
# Spec keys that drive the builder and are not level fields.
SPEC_ONLY_KEYS = {"base", "docSets", "kybType", "kybSettings"}

DEFAULT_IDENTITY_TYPES = ["PASSPORT", "ID_CARD", "DRIVERS", "RESIDENCE_PERMIT"]
DEFAULT_SELFIE_TYPES = ["SELFIE"]
DEFAULT_POR_TYPES = ["UTILITY_BILL"]

KYB_SET_TYPES = ("COMPANY_DATA", "COMPANY_DOCUMENTS", "COMPANY_BENEFICIARIES")
COMPANY_LEVEL_EXTRA_SET_TYPES = {
    "EMAIL_VERIFICATION", "PHONE_VERIFICATION", "PAYMENT_METHODS",
    "QUESTIONNAIRE", "QUESTIONNAIRE2", "QUESTIONNAIRE3", "QUESTIONNAIRE4",
}
KYB_TYPES = {"autoAndManual", "auto", "amlOnly"}
KYB_SETTINGS_KEYS = {
    "shareholderThreshold", "uboThreshold", "disableCompanySearchAndPrefill", "enableBeneficiariesAutoCheck",
}
DEFAULT_KYB_THRESHOLD = 25
# Level-wide spec keys copied into the payload as they are.
LEVEL_PASS_THROUGH_KEYS = (
    "desc", "websdkNext", "rejectUsaResidents", "crossCheckPresetId",
    "ipRestrictionSettings", "applicantInsightSettings",
    "deviceIntelligenceSettings", "kytSettings", "watchListCheckSettings",
    "useCustomWatchListCheckSettings", "disableWatchlists",
    "agreementSettings",
    "fraudPreventionSettings", "useCustomFraudPreventionSettings",
)
# Sumsub's own default company level — read-only for clients.
RESERVED_LEVEL_NAMES = {"company-zero"}

# The dashboard's COMPANY_DATA field list: company fields plus address fields.
COMPANY_DATA_FIELD_NAMES = {
    "companyName", "country", "registrationNumber", "registrationLocation", "type",
    "legalForm", "incorporatedOn", "alternativeNames", "legalAddress", "postalAddress",
    "controlScheme", "email", "phone", "taxId", "leiCode", "website",
    "street", "subStreet", "buildingNumber", "flatNumber", "town", "postCode", "state",
}
# The dashboard locks these as required (and, on COMPANY_DATA, prefilled).
LOCKED_COMPANY_FIELDS = ("country", "companyName")

# The subtypes the dashboard offers per group — a group's default subTypes and, for the named
# groups, all it allows. REGULATORY_LICENSE, TAX_CERT, ... are not supported by this skill yet.
COMPANY_DOCS_GROUP_SUB_TYPES = {
    "legalPresence": [
        "INCORPORATION_CERT", "INCORPORATION_ARTICLES", "STATE_REGISTRY",
        "PARTNERSHIP_AGREEMENT", "TRUST_AGREEMENT", "TRADE_LICENSE",
    ],
    "companyDetails": [
        "INFORMATION_STATEMENT", "PROOF_OF_ADDRESS", "STATE_REGISTRY", "INCORPORATION_ARTICLES",
        "INCORPORATION_CERT", "INCUMBENCY_CERT", "GOOD_STANDING_CERT", "PARTNERSHIP_AGREEMENT",
        "TRUST_AGREEMENT", "OWNERSHIP_STRUCTURE_CHART", "TRADE_LICENSE",
    ],
    "ownershipStructure": [
        "SHAREHOLDER_REGISTRY", "INFORMATION_STATEMENT", "TRUST_AGREEMENT", "INCUMBENCY_CERT",
        "STATE_REGISTRY", "PARTNERSHIP_AGREEMENT", "INCORPORATION_ARTICLES", "OWNERSHIP_STRUCTURE_CHART",
    ],
    "controlStructure": [
        "DIRECTORS_REGISTRY", "TRUST_AGREEMENT", "INCORPORATION_ARTICLES", "INCUMBENCY_CERT",
        "INFORMATION_STATEMENT", "STATE_REGISTRY", "PARTNERSHIP_AGREEMENT",
    ],
    "representativesAuthorization": [
        "POWER_OF_ATTORNEY", "DIRECTORS_REGISTRY", "STATE_REGISTRY", "INCORPORATION_CERT",
        "INCUMBENCY_CERT", "PARTNERSHIP_AGREEMENT",
    ],
    "other1": ["OTHER"],
    "other2": ["OTHER"],
    "other3": ["OTHER"],
}
DEFAULT_COMPANY_DOCS_GROUP = "legalPresence"
OTHER_DOCS_GROUP_LABELS = ("other1", "other2", "other3")
# An "Other" group takes OTHER plus any subtype of the named groups, as in the dashboard.
OTHER_DOCS_GROUP_SUB_TYPES = list(dict.fromkeys(
    ["OTHER"] + [sub_type for sub_types in COMPANY_DOCS_GROUP_SUB_TYPES.values() for sub_type in sub_types]
))

# The associated-party roles (CompanyBeneficiaryGroupCategory) this skill builds.
BENEFICIARY_CATEGORIES = (
    "ubos", "shareholders", "directors", "representatives",
    "companyOfficers", "secretaries", "founders", "investors", "legalAdvisors", "authorizedSignatories",
    "trustees", "trustBeneficiaries", "trustSettlors", "trustProtectors",
    "managingPartners", "equityPartners",
    "fundInvestors", "fundManagers", "investmentManagers", "investmentAdvisers", "fundAdministrators",
    "depositaries", "custodians", "primeBrokers",
)
UNSUPPORTED_BENEFICIARY_CATEGORIES = {"accountUsers"}
# Which party kinds a role takes, as in the dashboard: every role takes company parties except
# these; company parties for ubos / representatives are not supported by this skill yet.
INDIVIDUAL_ONLY_CATEGORIES = {"companyOfficers", "authorizedSignatories"}
UNSUPPORTED_COMPANY_PARTY_CATEGORIES = {"ubos", "representatives"}
COMPANY_ONLY_CATEGORIES = {"depositaries", "custodians", "primeBrokers"}
# The dashboard offers shareSize / natureOfControl on these roles and adds a required shareSize.
OWNERSHIP_CATEGORIES = {"ubos", "shareholders", "investors"}
# The dashboard lists these as "Internal use only • Not verified by Sumsub".
INTERNAL_CATEGORIES = {"companyOfficers", "investors"}
# The dashboard's structure types: it warns when one step mixes roles of more than one.
STRUCTURE_ROLE_GROUPS = {
    "company": {"ubos", "shareholders", "directors", "companyOfficers", "secretaries", "investors"},
    "trust": {"trustees", "trustBeneficiaries", "trustSettlors", "trustProtectors"},
    "partnership": {"managingPartners", "equityPartners"},
    "fund": {
        "fundInvestors", "fundManagers", "investmentManagers", "investmentAdvisers", "fundAdministrators",
        "depositaries", "custodians", "primeBrokers",
    },
}
ADDRESS_FIELD_NAMES = {
    "country", "street", "subStreet", "buildingNumber", "flatNumber", "town", "state", "postCode",
}
BENEFICIARY_FIELD_NAMES = {"shareSize", "natureOfControl"}
INDIVIDUAL_PARTY_FIELD_NAMES = {
    "firstName", "lastName", "middleName", "email", "phone", "countryOfBirth", "stateOfBirth",
    "dob", "placeOfBirth", "legalName", "gender", "nationality", "taxResidenceCountry", "tin",
} | ADDRESS_FIELD_NAMES
COMPANY_PARTY_FIELD_NAMES = {
    "companyName", "alternativeNames", "country", "registrationNumber", "registrationLocation",
    "type", "legalForm", "incorporatedOn", "legalAddress", "postalAddress", "controlScheme",
    "email", "phone", "taxId", "website", "leiCode",
} | ADDRESS_FIELD_NAMES
# The dashboard rejects an individual party unless one of these is a required field.
INDIVIDUAL_PARTY_CORE_FIELDS = {"firstName", "lastName", "email"}
PARTY_KEYS = {"enabled", "levelName", "fields", "customFields"}
ROLE_KEYS = {"category", "canSkip", "minRequired", "maxAllowed", "individual", "company"}
# How many parties of a role the applicant must / may add; unset means 1 / 100.
ROLE_LIMIT_MIN, ROLE_LIMIT_MAX = 1, 100
# Keys of ApplicantIdDocSetField / ApplicantIdDocSetCustomField.
FIELD_KEYS = {"name", "required", "prefill", "immutableIfPresent"}
CUSTOM_FIELD_KEYS = {"name", "displayName", "required", "immutableIfPresent"}


def _field_obj(f):
    if isinstance(f, str):
        return {"name": f, "required": True}
    if isinstance(f, dict) and "name" in f:
        return {**{"required": True}, **f}
    raise ValueError(f"field must be a string or object with 'name': {f!r}")


def _validate_check_source_settings(css, where):
    """Structural check for a checkSourceSettings block — resolved via
    sumsub-check-databases and attached either at level top level
    (validationReady placement) or nested inside a docSet (stepsReady
    placement). Shape: {countrySettings: [{country, executionConfigurations:
    [{sourceId, ...}], ...}]}."""
    if not isinstance(css, dict) or not isinstance(css.get("countrySettings"), list) or not css["countrySettings"]:
        raise ValueError(f"{where}: checkSourceSettings must be an object with a non-empty 'countrySettings' list")
    for entry in css["countrySettings"]:
        if not isinstance(entry, dict) or not entry.get("country"):
            raise ValueError(f"{where}: each checkSourceSettings.countrySettings entry needs a 'country'")
        exec_cfgs = entry.get("executionConfigurations")
        if not isinstance(exec_cfgs, list) or not exec_cfgs:
            raise ValueError(f"{where}: checkSourceSettings.countrySettings[{entry['country']!r}] needs a non-empty 'executionConfigurations' list")
        for cfg in exec_cfgs:
            if not isinstance(cfg, dict) or not cfg.get("sourceId"):
                raise ValueError(f"{where}: each executionConfigurations entry needs a 'sourceId'")
    return css


def _build_identity(spec):
    """IDENTITY(2/3/4) doc-set. See SKILL.md "Dashboard ↔ API mapping" for the
    label-to-value table. Defaults match the dashboard's Vue watcher in
    IdentityDocsStepCard.vue: on Live-capture toggle it writes
    `manualAndAuto`/`always`; on File-upload toggle it deletes both sub-options.
    Those defaults are not optional — without them the dashboard renders empty
    'Capture mode' / 'Fallback' dropdowns. NFC defaults to `disabled` for the
    same reason (otherwise the radio shows nothing selected)."""
    types = spec.get("docTypes") or DEFAULT_IDENTITY_TYPES
    video_required = spec.get("videoRequired") if spec.get("videoRequired") is not None else "disabled"
    if video_required not in IDENTITY_VIDEO_REQUIRED:
        raise ValueError(f"IDENTITY videoRequired must be one of {sorted(IDENTITY_VIDEO_REQUIRED)}; got {video_required!r}")

    out = {
        "idDocSetType": spec["type"],
        "types": list(types),
        "videoRequired": video_required,
    }

    if video_required == "docapture":
        capture_mode = spec.get("captureMode") if spec.get("captureMode") is not None else "manualAndAuto"
        if capture_mode not in CAPTURE_MODES:
            raise ValueError(f"IDENTITY captureMode must be one of {sorted(CAPTURE_MODES)}; got {capture_mode!r}")
        out["captureMode"] = capture_mode

        uploader_mode = spec.get("uploaderMode") if spec.get("uploaderMode") is not None else "always"
        if uploader_mode not in UPLOADER_MODES:
            raise ValueError(f"IDENTITY uploaderMode must be one of {sorted(UPLOADER_MODES)}; got {uploader_mode!r}")
        out["uploaderMode"] = uploader_mode
    # else: captureMode/uploaderMode silently dropped — matches the Vue watcher's
    # `delete` on toggle to File upload.

    nfc_settings = spec.get("nfcVerificationSettings")
    if nfc_settings is None:
        nfc_settings = {"mode": "disabled"}
    elif not isinstance(nfc_settings, dict):
        raise ValueError(f"IDENTITY nfcVerificationSettings must be a dict with a 'mode' key; got {nfc_settings!r}")
    else:
        mode = nfc_settings.get("mode")
        if mode not in NFC_MODES:
            raise ValueError(f"IDENTITY nfcVerificationSettings.mode must be one of {sorted(NFC_MODES)}; got {mode!r}")
    out["nfcVerificationSettings"] = nfc_settings

    # Non-doc-in-identity-step placement (source's stepsReady contains IDENTITY,
    # resolved via sumsub-check-databases) — applicant can upload a document OR
    # pass the database check, both live on this same docSet. `types` above is
    # untouched, so upload stays available.
    css = spec.get("checkSourceSettings")
    if css is not None:
        out["checkSourceSettings"] = _validate_check_source_settings(css, spec["type"])

    return out


def _build_selfie(spec):
    types = spec.get("docTypes") or DEFAULT_SELFIE_TYPES
    video_required = spec.get("videoRequired") or "passiveLiveness"
    if video_required not in SELFIE_VIDEO_REQUIRED:
        raise ValueError(f"SELFIE videoRequired must be one of {sorted(SELFIE_VIDEO_REQUIRED)}; got {video_required!r}")
    out = {
        "idDocSetType": spec["type"],
        "types": list(types),
        "videoRequired": video_required,
    }
    if spec.get("selfieProcessingSettings") is not None:
        sps = spec["selfieProcessingSettings"]
        if not isinstance(sps, dict):
            raise ValueError(f"SELFIE selfieProcessingSettings must be an object; got {sps!r}")
        out["selfieProcessingSettings"] = sps
    return out


def _build_por(spec):
    """PROOF_OF_RESIDENCE(2) doc-set. Accepts an optional POA preset id
    (`poaPresetId` friendly alias, or the canonical `poaStepSettingsId`).
    Pass the `id` returned by `sumsub-create-poa-preset` here to attach
    a preset to this level."""
    out = {
        "idDocSetType": spec["type"],
        "types": list(spec.get("docTypes") or DEFAULT_POR_TYPES),
    }
    poa_id = spec.get("poaPresetId") or spec.get("poaStepSettingsId")
    if poa_id is not None:
        if not isinstance(poa_id, str) or not poa_id.strip():
            raise ValueError(f"{spec['type']}: poaPresetId / poaStepSettingsId must be a non-empty string")
        out["poaStepSettingsId"] = poa_id.strip()
    return out


def _build_questionnaire(spec):
    """QUESTIONNAIRE(2/3/4) doc-set. Requires a questionnaire id (the slug
    returned as `id` by `sumsub-create-questionnaire`). Accepts both the
    canonical `questionnaireDefId` and the friendly `questionnaireId` alias."""
    qid = spec.get("questionnaireDefId") or spec.get("questionnaireId")
    if not qid:
        raise ValueError(f"{spec['type']} requires questionnaireDefId (or questionnaireId)")
    return {"idDocSetType": spec["type"], "questionnaireDefId": qid}


def _build_applicant_data(spec):
    fields = [_field_obj(f) for f in (spec.get("fields") or [])]
    return {"idDocSetType": "APPLICANT_DATA", "fields": fields}


def _build_payment(spec):
    """PAYMENT_METHODS doc-set for actionType='paymentMethod' action levels.
    Builds paymentSourceSettings from the compact typeSettings spec.
    walletScreeningProvider belongs at paymentSourceSettings level — NOT inside
    typeSettings.cryptoWallet. Cannot set both skip flags true simultaneously."""
    type_settings_in = spec.get("typeSettings") or {}
    type_settings_out = {}
    for type_name, type_cfg in type_settings_in.items():
        if not isinstance(type_cfg, dict):
            raise ValueError(f"PAYMENT_METHODS typeSettings.{type_name} must be an object; got {type_cfg!r}")
        if type_name == "bankCard":
            out_cfg = {"allowed": type_cfg.get("allowed", True)}
            count_images = type_cfg.get("countImages")
            if count_images is not None:
                if count_images not in BANK_CARD_COUNT_IMAGES:
                    raise ValueError(f"bankCard.countImages must be one of {sorted(BANK_CARD_COUNT_IMAGES)}; got {count_images!r}")
                out_cfg["countImages"] = count_images
            for k in ("extractIban", "extractNationalBankAccountNumbers", "requireBankAccountNumber"):
                if k in type_cfg:
                    out_cfg[k] = type_cfg[k]
            type_settings_out["bankCard"] = out_cfg
        elif type_name == "bankAccount":
            out_cfg = {"allowed": type_cfg.get("allowed", True)}
            for k in ("allowBankStatementUpload", "allowExternalSourcesCheck"):
                if k in type_cfg:
                    out_cfg[k] = type_cfg[k]
            # Unlike bankCard, an enabled bankAccount needs at least one concrete
            # verification method — `allowed: true` alone is rejected by the API.
            # The two methods: allowBankStatementUpload (document upload, no extra
            # entitlement) and allowExternalSourcesCheck (uses E_KYC entitlement).
            if out_cfg["allowed"] and not (
                out_cfg.get("allowBankStatementUpload") or out_cfg.get("allowExternalSourcesCheck")
            ):
                raise ValueError(
                    "PAYMENT_METHODS bankAccount: 'allowed: true' alone is rejected — enable at "
                    "least one verification method: allowBankStatementUpload (document upload, no "
                    "extra entitlement) and/or allowExternalSourcesCheck (requires E_KYC entitlement)"
                )
            type_settings_out["bankAccount"] = out_cfg
        elif type_name == "cryptoWallet":
            out_cfg = {"allowed": type_cfg.get("allowed", True)}
            form_type = type_cfg.get("unhostedWalletFormType")
            if form_type is not None:
                if form_type not in UNHOSTED_WALLET_FORM_TYPES:
                    raise ValueError(
                        f"cryptoWallet.unhostedWalletFormType must be one of {sorted(UNHOSTED_WALLET_FORM_TYPES)}; got {form_type!r}"
                    )
                out_cfg["unhostedWalletFormType"] = form_type
            if "satoshiTestAllowed" in type_cfg:
                out_cfg["satoshiTestAllowed"] = type_cfg["satoshiTestAllowed"]
            type_settings_out["cryptoWallet"] = out_cfg
        elif type_name == "eWallet":
            type_settings_out["eWallet"] = {"allowed": type_cfg.get("allowed", True)}
        else:
            type_settings_out[type_name] = type_cfg

    skip_ownership = spec.get("skipOwnershipCheck", False)
    skip_risk = spec.get("skipRiskScoreCheck", False)
    if skip_ownership and skip_risk:
        raise ValueError(
            "PAYMENT_METHODS: cannot set both skipOwnershipCheck and skipRiskScoreCheck to true simultaneously"
        )

    payment_source_settings = {"skipOwnershipCheck": skip_ownership}
    if skip_risk:
        payment_source_settings["skipRiskScoreCheck"] = True

    wallet_provider = spec.get("walletScreeningProvider")
    if wallet_provider is not None:
        if wallet_provider not in WALLET_SCREENING_PROVIDERS:
            raise ValueError(
                f"walletScreeningProvider must be one of {sorted(WALLET_SCREENING_PROVIDERS)}; got {wallet_provider!r}"
            )
        payment_source_settings["walletScreeningProvider"] = wallet_provider

    if type_settings_out:
        payment_source_settings["typeSettings"] = type_settings_out

    return {
        "idDocSetType": "PAYMENT_METHODS",
        "types": ["PAYMENT_SOURCE"],
        "paymentSourceSettings": payment_source_settings,
    }


def _kyb_fields(raw, allowed, where):
    if not isinstance(raw, list):
        raise ValueError(f"{where}: fields must be a list; got {raw!r}")
    fields = [_field_obj(f) for f in raw]
    for field in fields:
        bad_keys = sorted(set(field) - FIELD_KEYS)
        if bad_keys:
            raise ValueError(f"{where}: field {field['name']!r} has unsupported key(s) {bad_keys}; allowed: {sorted(FIELD_KEYS)}")
    names = [f["name"] for f in fields]
    unknown = sorted({n for n in names if n not in allowed})
    if unknown:
        raise ValueError(f"{where}: unknown field name(s) {unknown}; allowed: {sorted(allowed)}")
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ValueError(f"{where}: duplicate field name(s) {duplicates}")
    return fields


def _kyb_custom_fields(raw, field_names, where):
    if not isinstance(raw, list) or not all(isinstance(c, dict) and c.get("name") for c in raw):
        raise ValueError(f"{where}: customFields must be a list of objects with a 'name'; got {raw!r}")
    for custom in raw:
        bad_keys = sorted(set(custom) - CUSTOM_FIELD_KEYS)
        if bad_keys:
            raise ValueError(
                f"{where}: custom field {custom['name']!r} has unsupported key(s) {bad_keys}; allowed: {sorted(CUSTOM_FIELD_KEYS)}"
            )
    names = [c["name"] for c in raw] + list(field_names)
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise ValueError(f"{where}: customFields reuse field name(s) {duplicates}")
    return raw


def _lock_company_fields(fields, where, force_prefill):
    for name in reversed(LOCKED_COMPANY_FIELDS):
        field = next((f for f in fields if f["name"] == name), None)
        if field is None:
            fields.insert(0, {"name": name, "required": True, "prefill": True})
            continue
        if field.get("required") is False:
            raise ValueError(f"{where}: '{name}' is always required — the dashboard does not allow making it optional")
        if force_prefill:
            if field.get("prefill") is False:
                raise ValueError(f"{where}: '{name}' is always prefilled — the dashboard does not allow turning it off")
            field["prefill"] = True
    return fields


def _build_company_data(spec):
    where = "COMPANY_DATA"
    raw = spec.get("fields")
    if raw is None:
        fields = [{"name": n, "required": True, "prefill": True} for n in ("country", "companyName", "registrationNumber")]
    else:
        fields = _kyb_fields(raw, COMPANY_DATA_FIELD_NAMES, where)
    _lock_company_fields(fields, where, force_prefill=True)
    out = {"idDocSetType": "COMPANY_DATA", "fields": fields}
    if spec.get("customFields") is not None:
        out["customFields"] = _kyb_custom_fields(spec["customFields"], [f["name"] for f in fields], where)
    return out


def _build_company_documents(spec):
    raw = spec.get("companyDocsGroupDefinitions")
    if raw is None:
        raw = [{"label": DEFAULT_COMPANY_DOCS_GROUP}]
    if not isinstance(raw, list) or not raw:
        raise ValueError("COMPANY_DOCUMENTS: companyDocsGroupDefinitions must be a non-empty list of document groups")
    groups, seen = [], set()
    for group in raw:
        if not isinstance(group, dict):
            raise ValueError(f"COMPANY_DOCUMENTS: each document group must be an object; got {group!r}")
        unknown = sorted(set(group) - {"label", "subTypes", "required"})
        if unknown:
            raise ValueError(f"COMPANY_DOCUMENTS: unsupported group key(s) {unknown}; allowed: label, subTypes, required")
        label = group.get("label")
        if label not in COMPANY_DOCS_GROUP_SUB_TYPES:
            raise ValueError(f"COMPANY_DOCUMENTS: group label must be one of {list(COMPANY_DOCS_GROUP_SUB_TYPES)}; got {label!r}")
        if label in seen:
            raise ValueError(f"COMPANY_DOCUMENTS: duplicate document group {label!r}")
        seen.add(label)
        default = COMPANY_DOCS_GROUP_SUB_TYPES[label]
        allowed = OTHER_DOCS_GROUP_SUB_TYPES if label in OTHER_DOCS_GROUP_LABELS else default
        sub_types = group.get("subTypes")
        if sub_types is None:
            sub_types = list(default)
        if not isinstance(sub_types, list) or not sub_types:
            raise ValueError(f"COMPANY_DOCUMENTS group {label!r}: subTypes must be a non-empty list")
        not_offered = [s for s in sub_types if s not in allowed]
        if not_offered:
            raise ValueError(f"COMPANY_DOCUMENTS group {label!r}: {not_offered} not offered for this group; allowed: {allowed}")
        if len(set(sub_types)) != len(sub_types):
            raise ValueError(f"COMPANY_DOCUMENTS group {label!r}: duplicate subTypes {sub_types}")
        required = group.get("required", True)
        if not isinstance(required, bool):
            raise ValueError(f"COMPANY_DOCUMENTS group {label!r}: required must be true or false; got {required!r}")
        groups.append({"label": label, "subTypes": list(sub_types), "required": required})
    return {"idDocSetType": "COMPANY_DOCUMENTS", "companyDocsGroupDefinitions": groups}


def _default_party_fields(party, category):
    """The dashboard's default party fields."""
    if party == "individual":
        fields = [
            {"name": "firstName", "required": True, "prefill": True},
            {"name": "lastName", "required": True, "prefill": True},
            {"name": "middleName", "required": False, "prefill": True},
            {"name": "dob", "required": False, "prefill": True},
            {"name": "email", "required": True, "prefill": False},
            {"name": "phone", "required": True, "prefill": False},
        ]
    else:
        fields = [
            {"name": "country", "required": True, "prefill": True},
            {"name": "companyName", "required": True, "prefill": True},
            {"name": "registrationNumber", "required": True, "prefill": False},
        ]
    if category in OWNERSHIP_CATEGORIES:
        fields.append({"name": "shareSize", "required": True, "prefill": True})
    return fields


def _build_party(party, raw, category):
    where = f"COMPANY_BENEFICIARIES {category}.{party}"
    if not isinstance(raw, dict):
        raise ValueError(f"{where} must be an object; got {raw!r}")
    unknown = sorted(set(raw) - PARTY_KEYS)
    if unknown:
        raise ValueError(f"{where}: unsupported key(s) {unknown}; allowed: {sorted(PARTY_KEYS)}")
    enabled = raw.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError(f"{where}: enabled must be true or false; got {enabled!r}")
    out = {"enabled": enabled}

    level_name = raw.get("levelName")
    if level_name is not None:
        if not isinstance(level_name, str) or not level_name.strip():
            raise ValueError(f"{where}: levelName must be a non-empty level name (omit it to collect data only)")
        out["levelName"] = level_name.strip()

    allowed = INDIVIDUAL_PARTY_FIELD_NAMES if party == "individual" else COMPANY_PARTY_FIELD_NAMES
    if category in OWNERSHIP_CATEGORIES:
        allowed = allowed | BENEFICIARY_FIELD_NAMES
    if raw.get("fields") is not None:
        fields = _kyb_fields(raw["fields"], allowed, where)
    else:
        # A switched-off party keeps the default fields too, as in the dashboard: they show when it's switched on.
        fields = _default_party_fields(party, category)
    if party == "company":
        _lock_company_fields(fields, where, force_prefill=False)
    out["fields"] = fields

    if enabled:
        if not fields:
            raise ValueError(f"{where}: an enabled party needs at least one field")
        if party == "individual" and not any(
            f["name"] in INDIVIDUAL_PARTY_CORE_FIELDS and f.get("required") is True for f in fields
        ):
            raise ValueError(f"{where}: at least one of {sorted(INDIVIDUAL_PARTY_CORE_FIELDS)} must be a required field")

    if raw.get("customFields") is not None:
        out["customFields"] = _kyb_custom_fields(raw["customFields"], [f["name"] for f in fields], where)
    return out


def _build_company_beneficiaries(spec):
    raw = spec.get("companyBeneficiaryDefinitions")
    if not isinstance(raw, list) or not raw:
        raise ValueError(
            "COMPANY_BENEFICIARIES requires companyBeneficiaryDefinitions — a non-empty list of roles, "
            "e.g. [{'category': 'ubos', 'individual': {'levelName': '<individual KYC level>'}}]"
        )
    roles, seen = [], set()
    for role in raw:
        if not isinstance(role, dict):
            raise ValueError(f"COMPANY_BENEFICIARIES: each role must be an object; got {role!r}")
        unknown = sorted(set(role) - ROLE_KEYS)
        if unknown:
            raise ValueError(f"COMPANY_BENEFICIARIES: unsupported role key(s) {unknown}; allowed: {sorted(ROLE_KEYS)}")
        category = role.get("category")
        if category not in BENEFICIARY_CATEGORIES:
            if category in UNSUPPORTED_BENEFICIARY_CATEGORIES:
                raise ValueError(
                    f"COMPANY_BENEFICIARIES: role {category!r} is not supported by this skill — add it in the Sumsub dashboard"
                )
            raise ValueError(f"COMPANY_BENEFICIARIES: unknown role {category!r}; supported: {list(BENEFICIARY_CATEGORIES)}")
        if category in seen:
            raise ValueError(f"COMPANY_BENEFICIARIES: duplicate role {category!r}")
        seen.add(category)

        out = {"category": category}
        can_skip = role.get("canSkip")
        if can_skip is not None:
            if not isinstance(can_skip, bool):
                raise ValueError(f"COMPANY_BENEFICIARIES {category}: canSkip must be true or false; got {can_skip!r}")
            out["canSkip"] = can_skip
        for key in ("minRequired", "maxAllowed"):
            value = role.get(key)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int) or not ROLE_LIMIT_MIN <= value <= ROLE_LIMIT_MAX:
                raise ValueError(
                    f"COMPANY_BENEFICIARIES {category}: {key} must be a whole number from {ROLE_LIMIT_MIN} to {ROLE_LIMIT_MAX}; got {value!r}"
                )
            out[key] = value
        # A skippable role requires nothing, so its minRequired doesn't count.
        min_required, max_allowed = out.get("minRequired", ROLE_LIMIT_MIN), out.get("maxAllowed", ROLE_LIMIT_MAX)
        if not out.get("canSkip") and min_required > max_allowed:
            raise ValueError(
                f"COMPANY_BENEFICIARIES {category}: minRequired ({min_required}) must be <= maxAllowed ({max_allowed})"
            )
        for party in ("individual", "company"):
            if role.get(party) is not None:
                out[party] = _build_party(party, role[party], category)
        _check_party_kinds(category, out)
        # The dashboard's form needs every party kind the role takes, even one that is off — without
        # `individual` it fails with "Enable is required" and its options can't be picked.
        for party in _party_kinds(category):
            out.setdefault(party, _build_party(party, {"enabled": False}, category))
        roles.append(out)
    return {"idDocSetType": "COMPANY_BENEFICIARIES", "companyBeneficiaryDefinitions": roles}


def _party_kinds(category):
    """The party objects a role carries: `individual` on every role (company-only ones too, switched
    off), `company` on the roles whose company parties this skill builds."""
    if category in INDIVIDUAL_ONLY_CATEGORIES or category in UNSUPPORTED_COMPANY_PARTY_CATEGORIES:
        return ("individual",)
    return ("individual", "company")


def _check_party_kinds(category, role):
    """Which party kinds a role takes, per the dashboard matrix."""
    individual = role.get("individual", {}).get("enabled")
    company = role.get("company", {}).get("enabled")
    where = f"COMPANY_BENEFICIARIES {category}"
    if company and category in INDIVIDUAL_ONLY_CATEGORIES:
        raise ValueError(f"{where}: individual-only role — it takes no company parties")
    if company and category in UNSUPPORTED_COMPANY_PARTY_CATEGORIES:
        raise ValueError(f"{where}: company parties for {category} are not supported by this skill yet — add them in the Sumsub dashboard")
    if individual and category in COMPANY_ONLY_CATEGORIES:
        raise ValueError(f"{where}: company-only role — it takes no individual parties")
    if not individual and not company:
        kind = "'company'" if category in COMPANY_ONLY_CATEGORIES else "'individual' or 'company'"
        raise ValueError(f"{where}: enable at least one of {kind}")


def _build_kyb_settings(raw, kyb_type, is_create, base_settings=None):
    """kybSettings from the spec, laid over the current level's on update."""
    if raw is not None and not isinstance(raw, dict):
        raise ValueError(f"kybSettings must be an object; got {raw!r}")
    unknown = sorted(set(raw or {}) - KYB_SETTINGS_KEYS)
    if unknown:
        raise ValueError(f"kybSettings: unsupported key(s) {unknown}; supported: {sorted(KYB_SETTINGS_KEYS)}")
    if raw is None and base_settings is None and not is_create:
        return None
    settings = {**(base_settings or {}), **(raw or {})}
    for key in ("shareholderThreshold", "uboThreshold"):
        value = settings.get(key)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100):
            raise ValueError(f"kybSettings.{key} must be a number between 0 and 100; got {value!r}")
    if is_create:
        # 25 / 25 like the dashboard, but a lower UBO threshold alone lowers the shareholder one with it.
        if settings.get("uboThreshold") is None:
            settings["uboThreshold"] = DEFAULT_KYB_THRESHOLD
        if settings.get("shareholderThreshold") is None:
            settings["shareholderThreshold"] = min(DEFAULT_KYB_THRESHOLD, settings["uboThreshold"])
    shareholder, ubo = settings.get("shareholderThreshold"), settings.get("uboThreshold")
    if shareholder is not None and ubo is not None and shareholder > ubo:
        current = "" if is_create else ", ".join(
            f"{key} {settings[key]}" for key in ("shareholderThreshold", "uboThreshold") if key not in (raw or {})
        )
        hint = f" — the level has {current}; set both thresholds" if current else ""
        raise ValueError(f"kybSettings.shareholderThreshold ({shareholder}) must be <= uboThreshold ({ubo}){hint}")
    for key in ("disableCompanySearchAndPrefill", "enableBeneficiariesAutoCheck"):
        value = settings.get(key)
        if value is not None and not isinstance(value, bool):
            raise ValueError(f"kybSettings.{key} must be true or false; got {value!r}")
    if kyb_type == "amlOnly":
        if (raw or {}).get("disableCompanySearchAndPrefill") is False:
            raise ValueError("kybSettings.disableCompanySearchAndPrefill cannot be false with kybType 'amlOnly' — the dashboard forces company search off for AML-only KYB")
        if (raw or {}).get("enableBeneficiariesAutoCheck") is True:
            raise ValueError("kybSettings.enableBeneficiariesAutoCheck has no effect with kybType 'amlOnly' — AML-only KYB runs no registry check")
        settings["disableCompanySearchAndPrefill"] = True
    return settings


def _build_bare(spec):
    """Bare docSet for EMAIL_VERIFICATION / PHONE_VERIFICATION / DEVICE_CHECK / etc."""
    return {"idDocSetType": spec["type"]}


def _build_ekyc(spec):
    """E_KYC doc-set — standalone non-document identity verification (source's
    stepsReady contains E_KYC on its own, resolved via sumsub-check-databases).
    No document upload, so unlike IDENTITY there's no 'types' — the applicant
    supplies whatever requiredInputFields the check-source(s) need instead.
    checkSourceSettings is required: an E_KYC step with no source configured
    has nothing to verify the applicant against."""
    css = spec.get("checkSourceSettings")
    if css is None:
        raise ValueError(
            f"{spec['type']} requires checkSourceSettings — resolve a non-doc source via "
            "sumsub-check-databases and attach it here"
        )
    return {
        "idDocSetType": spec["type"],
        "checkSourceSettings": _validate_check_source_settings(css, spec["type"]),
    }


BUILDERS = {
    "IDENTITY": _build_identity, "IDENTITY2": _build_identity,
    "IDENTITY3": _build_identity, "IDENTITY4": _build_identity,
    "SELFIE": _build_selfie, "SELFIE2": _build_selfie,
    "PROOF_OF_RESIDENCE": _build_por, "PROOF_OF_RESIDENCE2": _build_por,
    "QUESTIONNAIRE": _build_questionnaire, "QUESTIONNAIRE2": _build_questionnaire,
    "QUESTIONNAIRE3": _build_questionnaire, "QUESTIONNAIRE4": _build_questionnaire,
    "APPLICANT_DATA": _build_applicant_data,
    "PAYMENT_METHODS": _build_payment,
    "E_KYC": _build_ekyc,
}
# KYB builders emit the complete docSet: no pass-through, unknown keys are rejected.
KYB_BUILDERS = {
    "COMPANY_DATA": (_build_company_data, {"type", "fields", "customFields"}),
    "COMPANY_DOCUMENTS": (_build_company_documents, {"type", "companyDocsGroupDefinitions"}),
    "COMPANY_BENEFICIARIES": (_build_company_beneficiaries, {"type", "companyBeneficiaryDefinitions"}),
}


def build_docset(spec):
    if not isinstance(spec, dict) or "type" not in spec:
        raise ValueError(f"docSet entry must have a 'type': {spec!r}")
    t = spec["type"]
    if t in UNSUPPORTED_SET_TYPES:
        raise ValueError(UNSUPPORTED_SET_TYPES[t])
    if t not in SET_TYPES:
        raise ValueError(f"unknown docSet type {t!r}; allowed: {sorted(SET_TYPES)}")

    if t in KYB_BUILDERS:
        # A step copied from the GET also carries its type as idDocSetType.
        if spec.get("idDocSetType") not in (None, t):
            raise ValueError(f"{t}: idDocSetType {spec['idDocSetType']!r} doesn't match type {t!r}")
        spec = {k: v for k, v in spec.items() if k != "idDocSetType"}
        kyb_builder, accepted = KYB_BUILDERS[t]
        unknown = sorted(set(spec) - accepted)
        if unknown:
            raise ValueError(f"{t}: unsupported key(s) {unknown}; accepted: {sorted(accepted)}")
        return kyb_builder(spec)

    # Removed compact-spec keys: catch old/stale specs before they slip through
    # the pass-through escape hatch and silently produce a wrong payload.
    if "inputType" in spec:
        raise ValueError(f"{t}: 'inputType' is no longer accepted (was a no-op — captureParams is @Transient server-side). Use 'videoRequired' instead: 'disabled' for File upload, 'docapture' for Live capture.")
    if "captureParams" in spec:
        raise ValueError(f"{t}: 'captureParams' is server-side @Transient and never persisted; use flat 'videoRequired' / 'captureMode' / 'uploaderMode' on the docSet instead.")

    builder = BUILDERS.get(t, _build_bare)
    out = builder(spec)

    # Pass-through any additional keys the caller supplied (escape hatch).
    handled = {
        "type", "docTypes", "videoRequired",
        "captureMode", "uploaderMode",
        "nfcVerificationSettings",
        "questionnaireDefId", "questionnaireId",
        "poaStepSettingsId", "poaPresetId",
        "fields", "paymentMethods",
        "selfieProcessingSettings",
        "typeSettings", "skipOwnershipCheck", "skipRiskScoreCheck", "walletScreeningProvider",
    }
    for k, v in spec.items():
        if k in handled or v is None:
            continue
        out[k] = v
    return out


def _keep_docset(entry, base):
    """{"type": T, "keep": true}: the current level's T step, copied as it is."""
    t = entry.get("type")
    if set(entry) != {"type", "keep"} or entry["keep"] is not True:
        raise ValueError(f"a keep entry is exactly {{'type': <step type>, 'keep': true}}; got {entry!r}")
    if base is None:
        raise ValueError(f"{t}: 'keep' copies the step from the current level — pass --base <GET response>")
    for ds in (base.get("requiredIdDocs") or {}).get("docSets") or []:
        if ds.get("idDocSetType") == t:
            return copy.deepcopy(ds)
    raise ValueError(f"{t}: nothing to keep — the current level has no {t} step")


def _check_base(spec, base, applicant_type):
    if base.get("applicantType") == "company":
        # Levels this skill doesn't update — whatever the change, KYB steps or not.
        if base.get("copyOf") is not None:
            raise ValueError(
                "this level is a copy of another account's level (copyOf) — it is read-only, and this skill makes no "
                "change to it; change the source level instead. Don't send the change any other way"
            )
        if base.get("websdkNext") is not True:
            raise ValueError(
                "this is a WebSDK 1.0 company level (legacy KYB) — this skill makes no change to it, not even to a "
                "non-KYB step. Make the change in the Sumsub dashboard; don't send it any other way"
            )
    base_applicant_type = base.get("applicantType") or "individual"
    if applicant_type != base_applicant_type:
        kind = "a company (KYB)" if base_applicant_type == "company" else f"an {base_applicant_type}"
        raise ValueError(f"this is {kind} level — applicantType {applicant_type!r} doesn't match it")
    if spec.get("id") and base.get("id") and spec["id"] != base["id"]:
        raise ValueError(f"spec id {spec['id']!r} is not the base level id {base['id']!r}")
    if spec.get("name") and base.get("name") and spec["name"] != base["name"]:
        raise ValueError(f"a level can't be renamed — the API keeps the name {base['name']!r}")


def _validate_fraud_prevention(spec):
    """Guard the two silent no-ops in the per-level Fraud Prevention override.

    The server reads `fraudPreventionSettings` only when
    `useCustomFraudPreventionSettings` is true, and it ignores unknown keys
    inside the object. Both mistakes return 200 with nothing applied, so they
    have to fail here instead.
    """
    # The server switches device intelligence off on every WebSDK 1.0 write, in either model.
    if (spec.get("deviceIntelligenceSettings") or {}).get("enabled") is True and spec.get("websdkNext") is False:
        raise ValueError(
            "deviceIntelligenceSettings.enabled applies to WebSDK 2.0 levels only; websdkNext must be true"
        )
    fp = spec.get("fraudPreventionSettings")
    if fp is None:
        return
    if not isinstance(fp, dict) or not fp:
        raise ValueError("fraudPreventionSettings must be a non-empty object")
    unknown = sorted(set(fp) - FRAUD_PREVENTION_CHECKS)
    if unknown:
        raise ValueError(
            f"unknown fraudPreventionSettings key(s): {unknown}; "
            f"valid keys are {sorted(FRAUD_PREVENTION_CHECKS)}"
        )
    non_bool = sorted(k for k, v in fp.items() if not isinstance(v, bool))
    if non_bool:
        raise ValueError(
            f"fraudPreventionSettings values must be true or false; got non-boolean for {non_bool}"
        )
    if spec.get("useCustomFraudPreventionSettings") is not True:
        raise ValueError(
            "fraudPreventionSettings is ignored unless useCustomFraudPreventionSettings is true: "
            "set it to true to override this level, or drop fraudPreventionSettings and let the "
            "level inherit the client-wide defaults (on a tenant moved to client-wide fraud "
            "prevention they start off, so check them first)"
        )
    if fp.get("deviceIntelligenceEnabled") is True and spec.get("websdkNext") is False:
        raise ValueError(
            "deviceIntelligenceEnabled applies to WebSDK 2.0 levels only; websdkNext must be true"
        )


def build_level(spec, base=None):
    """Full level payload from the compact spec. On update `base` is the level's current
    GET body — from --base, or the spec's own `base` key: the payload is then that level
    with the spec laid over it. Steps come from the spec (none given keeps the stored
    ones), requiredIdDocs keeps its other keys, kybSettings / autoCheckGeneratorSettings
    keep the base keys the spec doesn't set, built and spec values win over the rest."""
    spec_base = spec.get("base")
    if spec_base is not None:
        if base is not None:
            raise ValueError("pass the current level once — as --base or as the spec's base, not both")
        if not isinstance(spec_base, dict):
            raise ValueError("base must be the level object from the GET")
        if not spec.get("id"):
            raise ValueError("base is for updates only: the spec needs the level id too")
        base = spec_base
    if base is not None:
        # On update the spec leaves out what the user did not ask to change, so these
        # fields come from `base` before the defaults and checks below read them.
        spec = {**{k: base[k] for k in BASE_INHERITED if base.get(k) is not None}, **spec}
    name = spec.get("name") or (base or {}).get("name")
    if not name:
        raise ValueError("level spec must have a non-empty 'name'")
    if name in RESERVED_LEVEL_NAMES:
        raise ValueError(f"{name!r} is a reserved Sumsub level — never create or modify it; pick another name or level")
    applicant_type = spec.get("applicantType") or "individual"
    if applicant_type not in APPLICANT_TYPES:
        raise ValueError(f"applicantType must be one of {sorted(APPLICANT_TYPES)}; got {applicant_type!r}")
    if base is not None:
        _check_base(spec, base, applicant_type)
    elif applicant_type == "company" and spec.get("id"):
        raise ValueError(
            "updating a company (KYB) level needs its GET response as --base: PATCH replaces requiredIdDocs as a "
            "whole, so the builder lays the spec over the current level"
        )
    level_type = spec.get("type") or "standalone"
    if level_type not in LEVEL_TYPES:
        raise ValueError(f"level type must be one of {sorted(LEVEL_TYPES)}; got {level_type!r}")

    action_type = spec.get("actionType")
    if action_type is not None and action_type not in ACTION_TYPES:
        raise ValueError(f"actionType must be one of {sorted(ACTION_TYPES)}; got {action_type!r}")

    doc_sets_in = spec.get("docSets") or []
    # An update with no docSets keeps the stored steps as they are.
    if base is not None and not doc_sets_in:
        doc_sets_in = [
            {"type": ds.get("idDocSetType"), "keep": True}
            for ds in (base.get("requiredIdDocs") or {}).get("docSets") or []
        ]
    if not doc_sets_in:
        raise ValueError("level must have at least one docSet")

    # PAYMENT_METHODS runs in two modes: as a step in a normal level (no
    # actionType — just another docSet, no special handling), or as an action on
    # an actions-type level (actionType='paymentMethod'). Only the action form
    # carries structural constraints, and only the definitional ones: an action
    # runs on an 'actions' level, and a paymentMethod action needs the payment
    # docSet to act on.
    if action_type == "paymentMethod":
        if level_type != "actions":
            raise ValueError("actionType 'paymentMethod' requires level type 'actions'")
        input_types = {d.get("type") for d in doc_sets_in}
        if "PAYMENT_METHODS" not in input_types:
            raise ValueError("actionType 'paymentMethod' level must include a PAYMENT_METHODS docSet")

    doc_sets, kept = [], set()
    for d in doc_sets_in:
        if isinstance(d, dict) and "keep" in d:
            doc_sets.append(_keep_docset(d, base))
            kept.add(d["type"])
        else:
            doc_sets.append(build_docset(d))

    # Reject duplicate idDocSetType in the same level (Sumsub will too)
    seen = set()
    for ds in doc_sets:
        t = ds["idDocSetType"]
        if t in seen:
            raise ValueError(f"duplicate docSet type {t!r} in same level")
        seen.add(t)

    step_types = [ds["idDocSetType"] for ds in doc_sets]
    kyb_steps = [t for t in step_types if t in KYB_SET_TYPES]
    kyb_type = spec.get("kybType")
    kyb_settings = spec.get("kybSettings")
    if applicant_type == "company":
        if level_type != "standalone":
            raise ValueError("company (KYB) levels: only level type 'standalone' is supported by this skill")
        not_allowed = [
            t for t in step_types
            if t not in kept and t not in KYB_SET_TYPES and t not in COMPANY_LEVEL_EXTRA_SET_TYPES
        ]
        if not_allowed:
            raise ValueError(
                f"company (KYB) level cannot carry {not_allowed}; allowed steps: "
                f"{list(KYB_SET_TYPES) + sorted(COMPANY_LEVEL_EXTRA_SET_TYPES)}"
            )
        is_create = base is None
        # The skill's convention: a new company level starts with COMPANY_DATA, as one made in the
        # dashboard does. An update holds to it only as far as the current level does.
        base_steps = [ds.get("idDocSetType") for ds in ((base or {}).get("requiredIdDocs") or {}).get("docSets") or []]
        if "COMPANY_DATA" not in step_types and (is_create or "COMPANY_DATA" in base_steps):
            raise ValueError("company (KYB) level: COMPANY_DATA is required — this skill keeps the company information step")
        if step_types[0] != "COMPANY_DATA" and (is_create or base_steps[:1] == ["COMPANY_DATA"]):
            raise ValueError("company (KYB) level: COMPANY_DATA must be the first step — this skill starts company levels with it")
        if kyb_type is None and is_create:
            raise ValueError(
                "company (KYB) level needs kybType: 'autoAndManual' (Full KYB), 'auto' (Registry and AML Check) "
                "or 'amlOnly' (AML Check) — pick the mode the tenant's KYB entitlement allows"
            )
        if kyb_type is not None and kyb_type not in KYB_TYPES:
            raise ValueError(f"kybType must be one of {sorted(KYB_TYPES)}; got {kyb_type!r}")
        base_acgs = (base or {}).get("autoCheckGeneratorSettings") or {}
        base_kyb_settings = ((base or {}).get("requiredIdDocs") or {}).get("kybSettings")
        kyb_settings = _build_kyb_settings(
            kyb_settings, kyb_type or base_acgs.get("kybType"), is_create, base_kyb_settings,
        )
    else:
        if kyb_steps:
            raise ValueError(f"{kyb_steps} are KYB steps — set applicantType: 'company'")
        if kyb_type is not None or kyb_settings is not None:
            raise ValueError("kybType / kybSettings apply to company (KYB) levels only — set applicantType: 'company'")

    _validate_fraud_prevention(spec)

    payload = {
        "name": name,
        "type": level_type,
        "applicantType": applicant_type,
        "requiredIdDocs": {"docSets": doc_sets},
    }
    if kyb_settings is not None:
        payload["requiredIdDocs"]["kybSettings"] = kyb_settings
    if kyb_type is not None:
        payload["autoCheckGeneratorSettings"] = {
            **copy.deepcopy((base or {}).get("autoCheckGeneratorSettings") or {}), "kybType": kyb_type,
        }
    if action_type is not None:
        payload["actionType"] = action_type
    # Preserve id when provided — required for PATCH (update by id).
    # POST ignores id and assigns a fresh one, so passing it on create is harmless.
    if spec.get("id"):
        payload["id"] = spec["id"]
    # Optional level-wide pass-throughs
    for k in LEVEL_PASS_THROUGH_KEYS:
        if spec.get(k) is not None:
            payload[k] = spec[k]
    # Database-validation placement (source's validationReady is true, resolved
    # via sumsub-check-databases) — a level-wide sibling of `requiredIdDocs`,
    # NOT nested inside it. Cross-checks a document docSet that's still required.
    if spec.get("checkSourceSettings") is not None:
        payload["checkSourceSettings"] = _validate_check_source_settings(spec["checkSourceSettings"], "level")
    # WebSDK 2.0 is mandatory for NEW levels: default websdkNext to true on create
    # (no id in the spec) so a forgetful caller never ships a legacy WebSDK 1.0
    # level. On UPDATE (id present) leave it untouched — upgrading an existing
    # level's SDK is a heavy client migration, not something to force via a PATCH,
    # and omitting the field lets the server keep the level's current value. An
    # explicit websdkNext in the spec always wins, on create or update.
    if base is None and not spec.get("id"):
        payload.setdefault("websdkNext", True)
    # A top-level level field this builder does not model (customPrivacyLink, ...) passes
    # through as the spec sets it; server-populated fields and `_comment`-style keys never do.
    unmodeled = {k: v for k, v in spec.items()
                 if k not in payload and k not in SPEC_ONLY_KEYS and k not in SERVER_FIELDS
                 and not k.startswith("_") and v is not None}
    # On update the payload carries the whole level, and requiredIdDocs keeps its other
    # keys around the new docSets (a sent object replaces the stored one whole).
    if base is None:
        payload = {**payload, **unmodeled}
    else:
        payload = {
            **{k: copy.deepcopy(v) for k, v in base.items() if k not in SERVER_FIELDS},
            **payload,
            **unmodeled,
            "requiredIdDocs": {**copy.deepcopy(base.get("requiredIdDocs") or {}), **payload["requiredIdDocs"]},
        }
    if applicant_type == "company" and payload.get("websdkNext") is not True:
        raise ValueError(
            "company (KYB) levels are WebSDK 2.0 only — this skill doesn't build WebSDK 1.0 (legacy KYB) levels; "
            "leave websdkNext out of the spec"
        )
    return payload


def _spec_from_payload(payload, base):
    """The spec that would build `payload`: steps equal to the current level's are `keep`, the
    rest are rebuilt from their own keys; on update, settings equal to the current ones are left out."""
    base = base or {}
    base_steps = {ds.get("idDocSetType"): ds for ds in (base.get("requiredIdDocs") or {}).get("docSets") or []}
    required_id_docs = payload.get("requiredIdDocs")
    if required_id_docs is None and base:
        required_id_docs = base["requiredIdDocs"]
    if not isinstance(required_id_docs, dict):
        raise ValueError("the payload has no requiredIdDocs object")
    doc_sets = []
    for ds in required_id_docs.get("docSets") or []:
        if not isinstance(ds, dict):
            raise ValueError(f"docSet must be an object; got {ds!r}")
        t = ds.get("idDocSetType")
        if base and base_steps.get(t) == ds:
            doc_sets.append({"type": t, "keep": True})
        else:
            doc_sets.append({"type": t, **{k: v for k, v in ds.items() if k != "idDocSetType"}})
    spec = {"docSets": doc_sets}
    for key in ("id", "name", "applicantType", "type"):
        if payload.get(key) is not None:
            spec[key] = payload[key]
    for key in (*LEVEL_PASS_THROUGH_KEYS, "checkSourceSettings", "actionType"):
        if payload.get(key) is not None and payload[key] != base.get(key):
            spec[key] = payload[key]
    # Top-level fields the builder doesn't model pass through as the spec sets them.
    built = {"id", "name", "applicantType", "type", "requiredIdDocs", "autoCheckGeneratorSettings"}
    for key, value in payload.items():
        if key not in built and key not in spec and value is not None and value != base.get(key):
            spec[key] = value
    kyb_type = (payload.get("autoCheckGeneratorSettings") or {}).get("kybType")
    if kyb_type is not None and kyb_type != (base.get("autoCheckGeneratorSettings") or {}).get("kybType"):
        spec["kybType"] = kyb_type
    base_kyb_settings = (base.get("requiredIdDocs") or {}).get("kybSettings") or {}
    kyb_settings = required_id_docs.get("kybSettings")
    if isinstance(kyb_settings, dict):
        kyb_settings = {k: v for k, v in kyb_settings.items() if k not in base_kyb_settings or base_kyb_settings[k] != v}
    if kyb_settings:
        spec["kybSettings"] = kyb_settings
    return spec


def _diff_paths(a, b, path=""):
    """Where two JSON values differ, as dotted paths."""
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in sorted(set(a) | set(b), key=str) for p in _diff_paths(a.get(k), b.get(k), f"{path}.{k}" if path else str(k))]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in _diff_paths(x, y, f"{path}[{i}]")]
    return [] if a == b else [path or "(payload)"]


def check_payload(payload, base=None):
    """Refuse a company (KYB) level payload the builder wouldn't produce, so a payload the builder
    rejects — or one written by hand — can't reach the API. With `base` (the level's current GET
    response) the payload is a PATCH body: a key it leaves out keeps its current value, a key it
    sends must be what the builder makes of it."""
    if not isinstance(payload, dict):
        raise ValueError(f"the payload must be a level object; got {payload!r}")
    if (base or payload).get("applicantType") != "company":
        return
    rebuilt = build_level(_spec_from_payload(payload, base), base)
    if base is None:
        differ = _diff_paths(payload, rebuilt)
    else:
        differ = [p for k in payload for p in _diff_paths(payload[k], rebuilt.get(k), k)]
    if differ:
        shown = ", ".join(differ[:5]) + (f" (+{len(differ) - 5} more)" if len(differ) > 5 else "")
        raise ValueError(
            f"this payload is not what build_level.py builds — {shown} differ. Build company levels with "
            "build_level.py (--base for an update) and send its output unchanged; a setup the builder rejects "
            "can't be sent — change the request, or make that change in the Sumsub dashboard"
        )


def check_party_levels(payload, levels):
    """Every associated party's levelName names an existing standalone level of the party's kind.
    `levels` is the GET /resources/applicants/-/levels body. Returns notes for names it can't confirm."""
    items = (levels.get("list") or {}).get("items") or levels.get("items") or []
    total = (levels.get("list") or {}).get("totalItems", levels.get("totalItems"))
    complete = total is None or len(items) >= total
    by_name = {item.get("name"): item for item in items if isinstance(item, dict)}
    errors, notes = [], []
    for ds in payload.get("requiredIdDocs", {}).get("docSets") or []:
        for role in ds.get("companyBeneficiaryDefinitions") or []:
            for party in ("individual", "company"):
                cfg = role.get(party) or {}
                name = cfg.get("levelName")
                if not cfg.get("enabled", True) or not name:
                    continue
                where = f"COMPANY_BENEFICIARIES {role.get('category')}.{party}"
                level = by_name.get(name)
                if level is None:
                    if complete:
                        errors.append(
                            f"{where}: level {name!r} doesn't exist — create it first or pick an existing {party} level"
                        )
                    else:
                        notes.append(f"{where}: level {name!r} is not in the first page of the level list — check that it exists")
                elif level.get("applicantType") != party:
                    errors.append(f"{where}: {name!r} is a {level.get('applicantType')} level, so it can't verify {party} parties")
                elif level.get("type", "standalone") != "standalone":
                    errors.append(f"{where}: {name!r} is a level of type {level.get('type')!r} — parties need a standalone level")
    if errors:
        raise ValueError("; ".join(errors))
    return notes


def _load_response(path, flag):
    """A GET response as saved from get_level.sh (its trailing `HTTP <code>` line is ignored)."""
    with open(path, encoding="utf-8") as f:
        text = f.read().strip()
    lines = text.splitlines()
    if lines and re.fullmatch(r"HTTP \d{3}", lines[-1].strip()):
        if lines[-1].strip() != "HTTP 200":
            raise ValueError(f"{flag} {path}: the GET answered {lines[-1].strip()}, not HTTP 200")
        text = "\n".join(lines[:-1])
    try:
        body = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"{flag} {path}: not a JSON body ({e})")
    if not isinstance(body, dict):
        raise ValueError(f"{flag} {path}: expected a JSON object")
    return body


def _load_base(path):
    base = _load_response(path, "--base")
    if not base.get("id") or not isinstance(base.get("requiredIdDocs"), dict):
        raise ValueError(f"--base {path}: expected the GET /resources/applicants/-/levels/{{id}} body — a level with id and requiredIdDocs")
    return base


def _notes(payload, base):
    """Things the agent must tell the user; printed to stderr. They come from the final payload
    and, on update, from the steps it removes."""
    notes = []
    doc_sets = payload["requiredIdDocs"]["docSets"]
    if base is not None:
        types = {ds["idDocSetType"] for ds in doc_sets}
        removed = [
            ds.get("idDocSetType") for ds in base["requiredIdDocs"].get("docSets") or []
            if ds.get("idDocSetType") not in types
        ]
        if removed:
            notes.append(f"removes step(s) {removed} from the level — list them with keep: true to keep them")
    if payload.get("applicantType") != "company":
        return notes
    for ds in doc_sets:
        roles = ds.get("companyBeneficiaryDefinitions") or []
        for role in roles:
            if role.get("category") in INTERNAL_CATEGORIES:
                notes.append(f"{role['category']} is for internal use only — Sumsub does not verify these parties")
        groups = [g for g, members in STRUCTURE_ROLE_GROUPS.items() if any(r.get("category") in members for r in roles)]
        if len(groups) > 1:
            notes.append(
                f"the roles mix structure types ({', '.join(groups)}) — the dashboard warns about this; "
                "check that it matches the structure the user verifies"
            )
        if {"ubos", "shareholders"} <= {r.get("category") for r in roles if r.get("canSkip")}:
            notes.append(
                "canSkip is on both ubos and shareholders — the WebSDK lets the applicant skip only one of them: "
                "at least one owner must be declared"
            )
    if (payload.get("autoCheckGeneratorSettings") or {}).get("kybType") == "amlOnly":
        settings = payload["requiredIdDocs"].get("kybSettings") or {}
        if settings.get("enableBeneficiariesAutoCheck") is True:
            notes.append("kybSettings.enableBeneficiariesAutoCheck has no effect with kybType 'amlOnly' — AML-only KYB runs no registry check")
        base_settings = (base or {}).get("requiredIdDocs", {}).get("kybSettings") or {}
        if (base is not None and settings.get("disableCompanySearchAndPrefill") is True
                and base_settings.get("disableCompanySearchAndPrefill") is not True):
            notes.append("company search and prefill turn off: kybType 'amlOnly' sets kybSettings.disableCompanySearchAndPrefill to true")
    return notes


def main():
    parser = argparse.ArgumentParser(description="Build a Sumsub level payload from a compact spec on stdin.")
    parser.add_argument(
        "--base", metavar="FILE",
        help=(
            "update a level: FILE holds the level's GET response (the same as the spec's base); the output is that "
            "level with the spec laid over it. A copy of another account's company level and WebSDK 1.0 company "
            "levels are refused"
        ),
    )
    parser.add_argument(
        "--levels", metavar="FILE",
        help=(
            "the level list (list_levels.sh): every associated party's levelName must name an existing "
            "standalone level of the party's kind"
        ),
    )
    parser.add_argument(
        "--check", action="store_true",
        help=(
            "read a built payload instead of a spec and refuse a company (KYB) level payload build_level.py "
            "wouldn't produce (with --base: the PATCH body for that level). Prints nothing on success"
        ),
    )
    args = parser.parse_args()
    spec = _load_spec(sys.stdin)
    if not isinstance(spec, dict):
        raise ValueError(f"level {'payload' if args.check else 'spec'} must be an object; got {spec!r}")
    base = _load_base(args.base) if args.base else None
    if args.check:
        check_payload(spec, base)
        payload, notes = spec, []
    else:
        payload = build_level(spec, base)
        notes = _notes(payload, base if base is not None else spec.get("base"))
    if args.levels and (base or payload).get("applicantType") == "company":
        notes += check_party_levels(payload, _load_response(args.levels, "--levels"))
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    if not args.check:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
