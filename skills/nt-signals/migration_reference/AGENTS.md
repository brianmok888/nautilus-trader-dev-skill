# Signal Python Migration References

## OVERVIEW
Historical signal templates, examples and Python analysis mirror; score 9,
with a distinct migration domain beneath the current signal skill.

## WHERE TO LOOK
| Need | Location |
|------|----------|
| Python usage and extension context | `python/python-usage.md`, `python/python-extension.md` |
| Analyzer and statistic interfaces | `python/python/analysis/analyzer.py`, `python/python/analysis/statistic.py` |
| Reports and tearsheets | `python/python/analysis/reporter.py`, `python/python/analysis/tearsheet.py` |
| Themes and configuration | `python/python/analysis/themes.py`, `python/python/analysis/config.py` |
| Custom-data comparison | `python/templates/custom_data.py` |
| Indicator comparison | `python/templates/indicator.py` |
| Portfolio statistic comparison | `python/templates/portfolio_statistic.py` |
| Historical indicator flows | `python/examples/indicators/`, `python/examples/cascaded_indicators/` |
| Historical bar aggregation | `python/examples/bar_aggregation/` |

## CONVENTIONS
- Treat these files as comparison inputs when porting an existing system.
- Preserve each template's `TEMPLATE_CLASSIFICATION` header and source labels.
- The additional `python/python/analysis/` segment is the actual mirror layout.
- Read an example's README and runner together with its strategy file.
- Resolve the current statistic contract in the sibling Rust reference tree
  before transferring a Python statistic implementation.
- Separate custom-data JSON behavior from Arrow persistence behavior when
  replacing an old serialization example.

## ANTI-PATTERNS
- Offering these templates as the default for a new strategy or signal service.
- Copying a decorator or handler signature without checking its version.
- Assuming the Python analysis mirror defines the current Rust trait contract.
- Treating the presence of an example runner as evidence of a completed run.
