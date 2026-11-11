# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.25.0",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full", app_title="metasyn")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Metasyn - generate synthetic data
    """)
    return


@app.cell
async def _():
    import micropip

    await micropip.install("metasyn")
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import json

    from metasyn import MetaFrameBuilder, MetaFrame
    from metasyn.util import dtype_to_vartype, get_dtype
    from metasyn.registry import DistributionRegistry
    from collections import defaultdict

    return (
        DistributionRegistry,
        MetaFrame,
        MetaFrameBuilder,
        defaultdict,
        dtype_to_vartype,
        get_dtype,
        json,
        mo,
        np,
    )


@app.cell
def _(mo):
    initial_max_cols = 100
    get_col_state, set_col_state = mo.state(3)
    get_row_state, set_row_state = mo.state(10)
    get_max_col_state, set_max_col_state = mo.state(initial_max_cols)
    get_name_state, set_name_state = mo.state([""]*initial_max_cols)
    get_var_state, set_var_state = mo.state([None]*initial_max_cols)
    get_unq_state, set_unq_state = mo.state([False]*initial_max_cols)
    get_dist_state, set_dist_state = mo.state([None]*initial_max_cols)
    get_param_state, set_param_state = mo.state([{} for _ in range(initial_max_cols)])
    return (
        get_col_state,
        get_dist_state,
        get_name_state,
        get_param_state,
        get_row_state,
        get_unq_state,
        get_var_state,
        initial_max_cols,
        set_col_state,
        set_dist_state,
        set_max_col_state,
        set_name_state,
        set_param_state,
        set_row_state,
        set_unq_state,
        set_var_state,
    )


@app.cell
def _(
    set_dist_state,
    set_max_col_state,
    set_name_state,
    set_param_state,
    set_unq_state,
    set_var_state,
):
    def reset_max_cols(new_max_cols):
        set_max_col_state(new_max_cols)
        set_name_state([""]*new_max_cols)
        set_var_state([None]*new_max_cols)
        set_unq_state([False]*new_max_cols)
        set_dist_state([None]*new_max_cols)
        set_param_state([{} for _ in range(new_max_cols)])


    return (reset_max_cols,)


@app.cell
def _(set_dist_state, set_name_state, set_unq_state, set_var_state):
    def update_name_state(i, new_val):
        set_name_state(lambda cur: [
            new_val if idx == i else v for idx, v in enumerate(cur)
        ])
    def update_var_state(i, new_val):
        set_var_state(lambda cur: [
            new_val if idx == i else v for idx, v in enumerate(cur)
        ])
    def update_unq_state(i, new_val):
        set_unq_state(lambda cur: [
            new_val if idx == i else v for idx, v in enumerate(cur)
        ])
    def update_dist_state(i, new_val):
        set_dist_state(lambda cur: [
            new_val if idx == i else v for idx, v in enumerate(cur)
        ])

    return (
        update_dist_state,
        update_name_state,
        update_unq_state,
        update_var_state,
    )


@app.cell
def _(mo):
    file_ui = mo.ui.file(kind="area")
    return (file_ui,)


@app.cell
def _(
    MetaFrame,
    dtype_to_vartype,
    file_ui,
    json,
    np,
    reset_max_cols,
    set_col_state,
    set_row_state,
    update_dist_state,
    update_name_state,
    update_param_state,
    update_unq_state,
    update_var_state,
):
    def _sanitize_params(params):
        if "regex_data" in params:
            return {"regex_data": params["regex_data"]["regex"]}
        new_params = {}
        for name, val in params.items():
            new_val = val
            if isinstance(val, np.ndarray):
                new_val = ",".join(str(x) for x in val)
            new_params[name] = new_val
        return new_params


    def submit_file(clicked):
        if clicked and file_ui.contents() is not None:
            insert_file()

    def insert_file():
        data = file_ui.contents()
        mf_input = MetaFrame.load_json(json.loads(data.decode("utf-8")))
        reset_max_cols(mf_input.n_columns)
        set_row_state(mf_input.n_rows)
        set_col_state(mf_input.n_columns)
        for i, var in enumerate(mf_input.meta_vars):
            update_name_state(i, var.name)
            update_var_state(i, dtype_to_vartype(var.dtype))
            update_unq_state(i, var.distribution.unique)
            cur_dist_name = var.distribution.name[5:] if var.distribution.name.startswith("core.") else var.distribution.name
            update_dist_state(i, cur_dist_name)
            param_dict = var.distribution.to_dict()["parameters"]
            param_dict_sane = _sanitize_params(param_dict)
            for param_name, param_val in param_dict_sane.items():
                update_param_state(i, param_name, param_val, list(param_dict_sane))


    return (submit_file,)


@app.cell
def _(initial_max_cols, reset_max_cols, set_col_state, set_row_state):
    def reset(clicked):
        if clicked:
            reset_max_cols(initial_max_cols)
            set_col_state(3)
            set_row_state(10)


    return (reset,)


@app.cell
def _(file_ui, get_col_state, get_row_state, mo, set_col_state, set_row_state):
    if file_ui.contents() is None:
        col_form = mo.ui.slider(1, 20, value=get_col_state(), show_value=True, label="Number of columns:  ", on_change=set_col_state)
        row_form = mo.ui.number(1, value=get_row_state(), label="Number of rows:  ", on_change=set_row_state)
        col_row_man = mo.vstack([col_form, row_form])
    else:
        col_row_man = mo.md("Using GMF file, clear to set row, column manually.")
    return (col_row_man,)


@app.cell
def _(col_row_man, file_ui, mo, reset, submit_file):
    submit_gmf = mo.ui.run_button(on_change=submit_file, label="Submit GMF file")
    reset_button = mo.ui.run_button(on_change=reset, label="Reset")
    mo.vstack([mo.hstack([mo.vstack([file_ui, submit_gmf]), col_row_man], align="center", widths=[1,1]), reset_button], justify="center")
    return


@app.cell
def _():
    return


@app.cell
def _(get_param_state, set_param_state):

    def update_param_state(i, param_name, new_val, all_names):
        set_param_state(lambda cur: [
            {x: y for x, y in v.items() if x in all_names} | {param_name: new_val} if idx == i else v for idx, v in enumerate(cur)
        ])

    def update_param_defaults(i, default_params):
        cur_params = get_param_state()[i]
        if list(cur_params) == list(default_params):
            equal = True
            for par, def_par in zip(cur_params, default_params):
                if type(par) != type(def_par) and not (isinstance(par, (int, float)) and isinstance(def_par, (int, float))):
                    equal = False
                    break
            if equal:
                return
        set_param_state(lambda cur: [
            default_params if idx==i else v for idx, v in enumerate(cur)
        ])

    return update_param_defaults, update_param_state


@app.cell
def _(get_col_state, get_name_state, mo, update_name_state):
    name_array = mo.ui.array(
        [
            mo.ui.text(value=get_name_state()[i], on_change=lambda v, i=i: update_name_state(i, v))
            for i in range(get_col_state())
        ]
    )
    return (name_array,)


@app.cell
def _(get_col_state, get_var_state, mo, update_var_state):
    var_array = mo.ui.array(
        [
            mo.ui.dropdown(value=get_var_state()[i], options=["string", "categorical", "discrete", "date", "datetime", "time", "continuous"], on_change=lambda v, i=i: update_var_state(i, v))
            for i in range(get_col_state())
        ]
    )
    return (var_array,)


@app.cell
def _(get_col_state, get_unq_state, mo, update_unq_state):
    unq_array = mo.ui.array(
        [
            mo.ui.checkbox(value=get_unq_state()[i], label=f"Unique?", on_change=lambda v, i=i: update_unq_state(i, v))
            for i in range(get_col_state())
        ]
    )
    return (unq_array,)


@app.cell
def _(DistributionRegistry, defaultdict):
    reg = DistributionRegistry.parse("builtin")

    def get_distributions(var_type, unique):
        try:
            distributions = reg.filter_distributions(var_type=var_type, unique=unique)
        except:
            return {}
        res_dict = defaultdict(list)
        for dist in distributions:
            dist_name = dist.name[5:] if dist.name.startswith("core.") else dist.name
            if isinstance(dist.var_type, str):
                res_dict[dist_name].append(dist.var_type)
            else:
                res_dict[dist_name].extend(dist.var_type)
        return res_dict


    return get_distributions, reg


@app.cell
def _(
    get_col_state,
    get_dist_state,
    get_distributions,
    get_unq_state,
    get_var_state,
    mo,
    update_dist_state,
):
    dist_array = mo.ui.array(
        [
            mo.ui.dropdown(
                options=list(get_distributions(get_var_state()[i], get_unq_state()[i])),
                value=get_dist_state()[i] if get_dist_state()[i] in list(get_distributions(get_var_state()[i], get_unq_state()[i])) else None,
                on_change=lambda v, i=i: update_dist_state(i, v),
            )
            for i in range(get_col_state())
        ]
    )
    return (dist_array,)


@app.cell
def _(get_param_state, np, reg, update_param_defaults, update_param_state):
    def get_params(dist_name, var_type, unique, idx):
        try:
            dist = reg.find_distribution(dist_name, var_type=var_type, unique=unique)
        except ValueError:
            return
        default_params = dist.default_distribution().to_dict()["parameters"]
        if "regex_data" in default_params:
            default_params = {"regex_data": default_params["regex_data"]["regex"]}
        if "probs" in default_params and isinstance(default_params["probs"], np.ndarray):
            default_params = {key: ",".join(str(x) for x in val) for key, val in default_params.items()}
        update_param_defaults(idx, default_params)

        for param_name, default_val in default_params.items():
            cur_param_dict = get_param_state()[idx]
            if isinstance(default_val, np.ndarray):
                default_val = ",".join(str(x) for x in default_val)

            if param_name not in cur_param_dict:# or type(cur_param_dict[param_name] != type(default_val)):
                update_param_state(idx, param_name, default_val, list(default_params))
            val = get_param_state()[idx].get(param_name, default_val)
            options = []
            if isinstance(default_val, str) and dist.var_type == "datetime" and param_name in ["lower", "upper", "value"]:
                ui_type = "datetime"
            elif isinstance(default_val, str) and param_name == "faker_type":
                from faker import Faker
                locale = get_param_state()[idx].get("locale", "en_US")
                fake_list = dir(Faker(locale=locale))
                ui_type = "dropdown"
                options = [x for x in fake_list if not (x.startswith("_") or x in ['cache_pattern', 'factories', 'generator_attrs', 'items', 'locales', 'random', 'seed', 'seed_instance', 'seed_locale', 'weights', 'binary', 'enum',
                                                                                    'provider', 'providers'])]
            elif isinstance(default_val, str):
                ui_type = "text"
            elif isinstance(default_val, bool):
                ui_type = "checkbox"
            elif isinstance(default_val, (float, int)):
                ui_type = "number"
            elif isinstance(default_val, np.ndarray):
                ui_type = "text"
            else:
                raise ValueError("Not implemented type: ", type(default_val), default_val)
            yield ui_type, options, val, param_name, list(default_params)

    return (get_params,)


@app.cell
def _(
    get_col_state,
    get_dist_state,
    get_params,
    get_unq_state,
    get_var_state,
    mo,
    update_param_state,
):
    param_array_2 = mo.ui.array(
        [
            mo.ui.array([
                mo.ui.dropdown(options=options, value=default_val, label=param_name + ":", on_change=lambda v, idx=idx, param_name=param_name: update_param_state(idx, param_name, v, list(params))) if ui_type == "dropdown" else
                mo.ui.text(value=default_val, label=param_name + ":", on_change=lambda v, idx=idx, param_name=param_name: update_param_state(idx, param_name, v, list(params))) if ui_type == "text" else
                mo.ui.checkbox(value=default_val, label=param_name + ":", on_change=lambda v, idx=idx, param_name=param_name: update_param_state(idx, param_name, v, list(params))) if ui_type == "checkbox" else
                mo.ui.number(value=default_val, label=param_name, on_change=lambda v, idx=idx, param_name=param_name: update_param_state(idx, param_name, v, list(params))) if ui_type == "number" else
                mo.ui.datetime(value=default_val, label=param_name + ":", on_change=lambda v, idx=idx, param_name=param_name: update_param_state(idx, param_name, v, list(params))) if ui_type == "datetime" else None
                for ui_type, options, default_val, param_name, params in get_params(get_dist_state()[idx], var_type=get_var_state()[idx], unique=get_unq_state()[idx], idx=idx) if ui_type is not None
            ])
            for idx in range(get_col_state())
        ]
    )
    return (param_array_2,)


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Create columns with distributions

    To generate synthetic data select the following for each column:

    - Name of the column
    - Type of the variable, e.g. string, discrete, time.
    - Uniqueness, whether the column has unique values.
    - Distribution, such as normal, exponential. The available distributions are only shown after selecting the variable type.
    - Parameters of the distribution.
    """)
    return


@app.cell
def _(
    dist_array,
    get_col_state,
    mo,
    name_array,
    param_array_2,
    unq_array,
    var_array,
):

    mo.hstack(
        [
            mo.vstack([mo.md("Column name:")] + [name_array[i] for i in range(get_col_state())]),
            mo.vstack([mo.md("Variable type:")] + [var_array[i] for i in range(get_col_state())]),
            mo.vstack([mo.md("Uniqueness:")] + [unq_array[i] for i in range(get_col_state())]),
            mo.vstack([mo.md("Distribution:")] + [dist_array[i] for i in range(get_col_state())]),
            mo.vstack([mo.md("Parameters:")] + [param_array_2[i][0] if len(param_array_2[i]) > 0 else mo.md(" - ") for i in range(get_col_state())]),
            mo.vstack([mo.md(" - ")] + [param_array_2[i][1] if len(param_array_2[i]) > 1 else mo.md(" - ") for i in range(get_col_state())]),
            mo.vstack([mo.md(" - ")] + [param_array_2[i][2] if len(param_array_2[i]) > 2 else mo.md(" - ") for i in range(get_col_state())]),
            mo.vstack([mo.md(" - ")] + [param_array_2[i][3] if len(param_array_2[i]) > 3 else mo.md(" - ") for i in range(get_col_state())]),
        ]
    )
    return


@app.class_definition
class NoProgressBar():
    def update(self, val):
        pass
    def close(self):
        pass
    def set_description(self, desc):
        pass


@app.cell
def _(
    MetaFrameBuilder,
    dist_array,
    get_col_state,
    get_dtype,
    get_param_state,
    get_row_state,
    get_var_state,
    name_array,
    np,
    unq_array,
):
    builder = MetaFrameBuilder()
    builder.n_rows = get_row_state()
    for col_id in range(get_col_state()):
        name = name_array[col_id].value
        name = f"Column {col_id}" if name == "" else name
        var_type = get_var_state()[col_id]
        dist_name = dist_array[col_id].value
        unique = unq_array[col_id].value
        parameters = get_param_state()[col_id]
        if var_type is None or dist_name is None or parameters is None:
            var_type = "string"
            dist_name = "na"
            parameters = {}
            unique = False
        if dist_name == "multinoulli":
            parameters = {key: np.array(val.split(",")) for key, val in parameters.items()}
            parameters["probs"] = parameters["probs"].astype(float)
        builder.add_column(name=name)
        builder[name].distribution = {"name": dist_name, "unique": unique, "parameters": parameters}
        builder[name].dtype = get_dtype(var_type)
    mf = builder.fit(progress_bar=NoProgressBar())
    mf.synthesize(progress_bar=NoProgressBar())
    return (mf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Generate a GMF file

    Below you can generate a GMF (Generative Metadata Format) file. This file can be used to generate synthetic data. You can also generate synthetic data immediately one paragraph below.
    """)
    return


@app.cell
def _(json, mf, mo):
    from metasyn.metaframe import _jsonify

    def _to_json(mf):
        mf_dict = _jsonify(mf.to_dict())
        return json.dumps(mf_dict, indent=4).encode("utf-8")


    mo.download(
        data=_to_json(mf),
        filename="gmf.json",
        mimetype="application/json",
        label="Generate GMF file"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Generate a CSV file

    With the button below you can download the CSV file with synthetic data.
    """)
    return


@app.cell
def _(mf, mo):
    from metasyn.file import CsvFileInterface
    from io import BytesIO

    def _gen_csv(mf):
        handler = BytesIO()
        mf.write_synthetic(handler, file_format=CsvFileInterface.default_interface("synthetic.csv").to_dict(), progress_bar=NoProgressBar())
        return handler

    mo.download(
        data=_gen_csv(mf),
        filename="synthetic.csv",
        mimetype="text/csv",
        label="Generate CSV",
    )
    return


if __name__ == "__main__":
    app.run()
