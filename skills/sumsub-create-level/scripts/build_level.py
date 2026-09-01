#!/usr/bin/env python3
"""
Expand a compact level spec (JSON or YAML on stdin) into a full Sumsub
`ApplicantLevel` payload (JSON on stdout).

YAML support requires PyYAML (`pip install pyyaml`). If PyYAML is not
installed, only JSON input is accepted.

See SKILL.md for the spec format; this builder pads sensible defaults
per docSet type, validates enums, and passes unknown keys through.
"""
import json
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
    "COMPANY", "ACCREDITED_INVESTOR", "E_SIGN",
    "QUESTIONNAIRE", "QUESTIONNAIRE2", "QUESTIONNAIRE3", "QUESTIONNAIRE4",
    "E_KYC", "OTHER_DOCS", "COMPANY_DATA", "COMPANY_DOCUMENTS",
    "COMPANY_BENEFICIARIES", "TR_RECIPIENT_INFORMATION", "DEVICE_CHECK",
    "SOLANA_ATTESTATION", "LINEA_ATTESTATION", "CHAINLINK_ATTESTATION",
}
LEVEL_TYPES = {"standalone", "actions", "module"}
APPLICANT_TYPES = {"individual", "company"}
ACTION_TYPES = {"paymentMethod"}
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

DEFAULT_IDENTITY_TYPES = ["PASSPORT", "ID_CARD", "DRIVERS", "RESIDENCE_PERMIT"]
DEFAULT_SELFIE_TYPES = ["SELFIE"]
DEFAULT_POR_TYPES = ["UTILITY_BILL"]


def _field_obj(f):
    if isinstance(f, str):
        return {"name": f, "required": True}
    if isinstance(f, dict) and "name" in f:
        return {**{"required": True}, **f}
    raise ValueError(f"field must be a string or object with 'name': {f!r}")


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


def _build_company(spec):
    steps_in = spec.get("steps") or []
    if not steps_in:
        raise ValueError("COMPANY requires at least one step")
    steps = []
    for s in steps_in:
        if "name" not in s:
            raise ValueError(f"COMPANY step missing 'name': {s!r}")
        steps.append({
            "name": s["name"],
            "minDocsCnt": s.get("minDocsCnt", 1 if s["name"] == "company" else 0),
            "applicantLevelName": s.get("applicantLevelName"),
            "idDocTypes": s.get("idDocTypes"),
            "idDocSubTypes": s.get("idDocSubTypes"),
            "fields": [_field_obj(f) for f in (s.get("fields") or [])] or None,
            "customFields": s.get("customFields"),
            "captureMode": s.get("captureMode"),
        })
    return {
        "idDocSetType": "COMPANY",
        "types": ["COMPANY_DOC"],
        "steps": steps,
    }


def _build_bare(spec):
    """Bare docSet for EMAIL_VERIFICATION / PHONE_VERIFICATION / DEVICE_CHECK / etc."""
    return {"idDocSetType": spec["type"]}


BUILDERS = {
    "IDENTITY": _build_identity, "IDENTITY2": _build_identity,
    "IDENTITY3": _build_identity, "IDENTITY4": _build_identity,
    "SELFIE": _build_selfie, "SELFIE2": _build_selfie,
    "PROOF_OF_RESIDENCE": _build_por, "PROOF_OF_RESIDENCE2": _build_por,
    "QUESTIONNAIRE": _build_questionnaire, "QUESTIONNAIRE2": _build_questionnaire,
    "QUESTIONNAIRE3": _build_questionnaire, "QUESTIONNAIRE4": _build_questionnaire,
    "APPLICANT_DATA": _build_applicant_data,
    "PAYMENT_METHODS": _build_payment,
    "COMPANY": _build_company,
}


def build_docset(spec):
    if not isinstance(spec, dict) or "type" not in spec:
        raise ValueError(f"docSet entry must have a 'type': {spec!r}")
    t = spec["type"]
    if t not in SET_TYPES:
        raise ValueError(f"unknown docSet type {t!r}; allowed: {sorted(SET_TYPES)}")

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
        "fields", "paymentMethods", "steps",
        "selfieProcessingSettings",
        "typeSettings", "skipOwnershipCheck", "skipRiskScoreCheck", "walletScreeningProvider",
    }
    for k, v in spec.items():
        if k in handled or v is None:
            continue
        out[k] = v
    return out


def build_level(spec):
    if "name" not in spec or not spec["name"]:
        raise ValueError("level spec must have a non-empty 'name'")
    applicant_type = spec.get("applicantType", "individual")
    if applicant_type not in APPLICANT_TYPES:
        raise ValueError(f"applicantType must be one of {sorted(APPLICANT_TYPES)}; got {applicant_type!r}")
    level_type = spec.get("type", "standalone")
    if level_type not in LEVEL_TYPES:
        raise ValueError(f"level type must be one of {sorted(LEVEL_TYPES)}; got {level_type!r}")

    action_type = spec.get("actionType")
    if action_type is not None and action_type not in ACTION_TYPES:
        raise ValueError(f"actionType must be one of {sorted(ACTION_TYPES)}; got {action_type!r}")

    doc_sets_in = spec.get("docSets") or []
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

    doc_sets = [build_docset(d) for d in doc_sets_in]

    # Reject duplicate idDocSetType in the same level (Sumsub will too)
    seen = set()
    for ds in doc_sets:
        t = ds["idDocSetType"]
        if t in seen:
            raise ValueError(f"duplicate docSet type {t!r} in same level")
        seen.add(t)

    payload = {
        "name": spec["name"],
        "type": level_type,
        "applicantType": applicant_type,
        "requiredIdDocs": {"docSets": doc_sets},
    }
    if action_type is not None:
        payload["actionType"] = action_type
    # Preserve id when provided — required for PATCH (update by id).
    # POST ignores id and assigns a fresh one, so passing it on create is harmless.
    if spec.get("id"):
        payload["id"] = spec["id"]
    # Optional level-wide pass-throughs
    for k in (
        "desc", "websdkNext", "rejectUsaResidents", "crossCheckPresetId",
        "ipRestrictionSettings", "applicantInsightSettings",
        "deviceIntelligenceSettings", "kytSettings", "watchListCheckSettings",
        "useCustomWatchListCheckSettings", "disableWatchlists",
        "agreementSettings", "checkSourceSettings",
    ):
        if spec.get(k) is not None:
            payload[k] = spec[k]
    # WebSDK 2.0 is mandatory for NEW levels: default websdkNext to true on create
    # (no id in the spec) so a forgetful caller never ships a legacy WebSDK 1.0
    # level. On UPDATE (id present) leave it untouched — upgrading an existing
    # level's SDK is a heavy client migration, not something to force via a PATCH,
    # and omitting the field lets the server keep the level's current value. An
    # explicit websdkNext in the spec always wins, on create or update.
    if not spec.get("id"):
        payload.setdefault("websdkNext", True)
    return payload


def main():
    spec = _load_spec(sys.stdin)
    payload = build_level(spec)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
