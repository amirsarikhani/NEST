# MESSAGEix

MESSAGEix, dynamic systems-optimization Integrated Assessment Model (see [Documentation](https://messageix.iiasa.ac.at/) )

This folder contains a version of the MESSAGEix GAMS code slightly adapted with particular features, such as inter-temporal storage.

The R scripts elaborate input data to produce `.gdx` files in `model\data` and run the GAMS model.
Oputput `.gdx` files are in `model\output`

## Data
Due to data sharing restrictions, procesed data used as model input is included in `NEST_Indus_SSP2_RPC6.RData`

## Run scenarios
To run pre-prepared scenarios, or change various pre-defined assumptions, opend and run the script `multiple_scenario_new.r`
