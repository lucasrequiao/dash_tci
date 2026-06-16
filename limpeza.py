import pandas as pd  # pyright: ignore[reportMissingImports]

def limpar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.rename(columns = {"Unnamed: 10": "email_estabelecimento"})
    # TODO limpeza de placeholder de email naoforneceuemail@gmail.com

    df["infracaoObservada"] = df["infracaoObservada"].replace({
        "DISTRIBUIDORA SEM ALVARÁ E FORA DO HORÁRIO": "DISTRIBUIDORA SEM ALVARÁ E FORA DO HORÁRIO DE FUNCIONAMENTO"         
    })

    df["dataCadastro"] = pd.to_datetime(df["dataCadastro"], errors="coerce")
    df["mes"] = df["dataCadastro"].dt.to_period("M").dt.to_timestamp()
    df["mes_label"] = df["dataCadastro"].dt.strftime("%Y-%m")

    # captura tudo antes da vírgula (nome) e os dígitos depois de "MATRICULA:"
    extraido = df["responsavel"].str.extract(r"^(?P<responsavel_nome>.*?),\s*MATRICULA:\s*(?P<responsavel_matricula>\d+)")
    nome = extraido["responsavel_nome"].str.strip()
    df["responsavel_nome"] = nome.replace({"NULL": pd.NA, "": pd.NA})
    base = df["Matrícula/PM"].astype("string").str.strip()
    do_resp = extraido["responsavel_matricula"].astype("string").str.strip()
    df["matricula_pm"] = base.replace({"": pd.NA}).fillna(do_resp)
    df = df.drop(columns=["responsavel", "Matrícula/PM"])

    # chave do estabelecimento para contar reincidência
    df["chave_estabelecimento"] = df["CPF/CNPJ"].astype("string").str.strip()
    # classificação PF/PJ (11 -> CPF, 14 -> CNPJ, resto -> Indefinido)
    digitos = df["chave_estabelecimento"].str.replace(r"\D", "", regex=True)
    n = digitos.str.len()
    df["tipo_doc"] = "Indefinido"
    df.loc[n == 11, "tipo_doc"] = "PF"
    df.loc[n == 14, "tipo_doc"] = "PJ"

    return df