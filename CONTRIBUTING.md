# Contributing

Mappings live in plain YAML so that risk and compliance people can review and
propose changes without touching code.

## Add or change a mapping

1. Edit the control in `data/controls.yaml` (add the item id under the right
   framework key in `maps`).
2. Run `python -m crosswalk validate` - it rejects ids that don't exist.
3. Run `python -m pytest -q` and `python -m crosswalk build`.
4. In the pull request, explain *why* the control supports the requirement.

**Mapping rule of thumb:** map a control to an item only if implementing the
control would produce evidence an auditor could point to for that item.
"Loosely related" is not enough.

## Add a new framework (e.g. NIST AI RMF)

1. Create `data/frameworks/<name>.yaml` with `id`, `name`, `short`, `kind`,
   `version`, `source_url`, `licence_note` and `items` (each with a unique `id`
   and `title`). Item ids must be unique across all frameworks.
2. Add the id to `FRAMEWORK_ORDER` in `crosswalk/model.py`, the `--to` choices
   in `crosswalk/__main__.py`, and a `--fw-<ID>` colour in
   `dashboard/template.html` (light and dark blocks).
3. Map existing controls to the new items, then validate and build.

## Copyright

Do not paste copyrighted control or clause text (ISO in particular). Use
identifiers, short titles and your own paraphrase.
