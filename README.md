## Dependencies
Dependencies of this project which are not part of the python std lib should be documented in the `requirements.txt` file.

## Setup
With pip:

```
pip install -r requirements.txt
```

With conda (alternative):

You need anaconda installed in your system. A recommended configuration
is to set the automatic activation of the `base` env to false,
running:

```
conda config --set auto_activate_base False
```

Using the `enviroment.yml` you can create the new env.

1. Create the environment using:
   ```
   conda env create -f environment.yml
   ```
2. Activate the environment
   ```
   conda activate ir-backend
   ```

## API Server

Run the server with:

```
uvicorn api:app --reload
```
