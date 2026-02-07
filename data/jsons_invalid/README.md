# Invalid Test Data

Test datasets with intentionally wrong values to verify the QA system catches errors.

## Files

**test_invalid_yesno.json**
Minimal test data with 6 wrong Yes/No answers for testing QA validation. Only includes data types that have prompts configured.

## How to Use

Open `notebooks/test_false_positives.ipynb` and run all cells. The notebook will upload the invalid data and show which values the QA system rejects.

## Invalid Data

test_invalid_yesno.json has these wrong values:

nuclearEnergyRelatedActivitiesSection426: Yes (should be No)
nuclearEnergyRelatedActivitiesSection427: Yes (should be No)
nuclearEnergyRelatedActivitiesSection428: No (should be Yes)
fossilGasRelatedActivitiesSection429: No (should be Yes)
fossilGasRelatedActivitiesSection430: No (should be Yes)
fossilGasRelatedActivitiesSection431: Yes (should be No)