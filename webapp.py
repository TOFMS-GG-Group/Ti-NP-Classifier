import streamlit as st
from helper import *
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme()
import plotly.express as px
import xarray as xr

st.title("Titanium engineered and natural particle types classifier.")
st.write("---" * 134)

''
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')


with st.sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 300px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 300px;
            margin-left: -300px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.header("File upload")
    file_type = st.radio(
        "Select upload file type",
        ('CSV','Excel'))
    if file_type == "Excel":
        tabname = st.text_input('Enter excel sheet name')
        st.session_state["uploaded_file"] = "init_xlsx"
        if tabname:
            st.session_state["uploaded_file"] = "xlsx"
            uploaded_file = st.file_uploader("Upload CSV/XLSX file", type=['xlsx'], accept_multiple_files=False)

    elif file_type == "CSV":
        st.session_state["uploaded_file"] = "CSV"
        tabname = st.text_input('FileNameDescription')
        uploaded_file = st.file_uploader("Upload CSV/XLSX file", type=['CSV'], accept_multiple_files=False)

    st.header("XD_Ti-TiNb")
    PartTypeXD = st.number_input(
        "Define the particle-type detection limit in attogram for classification of Ti-smNPs as ENPs")

# to handle session and UI
if st.session_state["uploaded_file"] == "xlsx" and uploaded_file is not None:
    file_details = {"name": uploaded_file.name, "type": uploaded_file.type, "proceed": True}
elif st.session_state["uploaded_file"] == "CSV" and uploaded_file is not None:
    file_details = {"name": uploaded_file.name, "type": uploaded_file.type, "proceed": True}
else:
    file_details = {"proceed": False}

def classifiers(dataframe,Xd):
    result_classify = []
    for index, row in dataframe.iterrows():
        if row["Ti"] > 0:
            if row["Ti"] > Xd and (row["Fe"] == 0 and row["Al"] == 0 and
                                           row["Mn"] == 0 and row["Nb"] == 0 and row["La"] == 0):
                     result_classify.append("E171")
            elif 0 < row["Ti"] < Xd and (row["Fe"] == 0 and row["Al"] == 0 and
                                           row["Mn"] == 0 and row["Nb"] == 0 and row["La"] == 0):
                     result_classify.append("unc sm-Ti")

            elif row["Ti"] > 0:
                if (row["Fe"] / row["Ti"]) > 10 and row["La"] == 0:
                    result_classify.append("Biotite")
                elif 0.75 < (row["Fe"] / row["Ti"]) < 5:
                    result_classify.append("Ilmenite")
                elif 0 < (row["Fe"] / row["Ti"]) < 0.1:
                    result_classify.append("Rutile")
                elif 0 < (row["Fe"] / row["Ti"]) < 0.75 and (row["Ti"] / row["Nb"]) > 300:
                    result_classify.append("Rutile")
                elif row["La"] > 0 and 0.75 < (row["Fe"] / row["Ti"]) < 5:
                    result_classify.append("Ilmenite")
                elif row["La"] > 0 and row["Mn"] == 0:
                    result_classify.append("Rutile")
                else:
                    result_classify.append("unc mm-Ti")

            else:
                result_classify.append("unclassified")
        else:
            result_classify.append("non Ti NPs")


    return pd.DataFrame(result_classify, columns=["classification"])


if file_details["proceed"]:
    try:
        print(file_details)
        saved_file = savefileindrive(uploaded_file)
        if saved_file == 1:
            print(f"Reading...{file_details['name']}..{tabname}")
            try:
                if uploaded_file.name.split(".")[1] == "csv":
                    dataframe = pd.read_csv(f"data/{file_details['name']}")
                elif uploaded_file.name.split(".")[1] == "xlsx":
                    dataframe = pd.read_excel(f"data/{file_details['name']}", sheet_name=f"{tabname}")
                st.write(dataframe)
                # st.subheader("Select columns:")
                # filtered = st.multiselect("Filter columns",options=list(dataframe.columns))
                # st.write(filtered)
                classifiedres = classifiers(
                    dataframe=dataframe[['Mg', 'Al', 'Ti', 'V', 'Mn',
                                         'Fe', 'Y', 'Zr',
                                        'Nb', 'La', 'Ce', 'Ta', ]], Xd=PartTypeXD)

                classified_combined = pd.concat([dataframe, pd.DataFrame(classifiedres, columns=["classification"])],
                                                axis=1)
                csvresult = convert_df(classified_combined)
                st.subheader("Classified result")
                st.write(classified_combined)
                ####### PIE chart#################
                st.write("All NPs including Non-Ti NPs")

                enp = classified_combined[classified_combined["classification"] == "E171"]["classification"].count()
                Rutile = classified_combined[classified_combined["classification"] == "Rutile"][
                    "classification"].count()
                Biotite = classified_combined[classified_combined["classification"] == "Biotite"][
                    "classification"].count()
                Ilmenite = classified_combined[classified_combined["classification"] == "Ilmenite"][
                    "classification"].count()
                uncsmNP = classified_combined[classified_combined["classification"] == "unc sm-Ti"][
                    "classification"].count()
                unclassified = classified_combined[classified_combined["classification"] == "unclassified"][
                    "classification"].count()
                unclassifiedmmNP = \
                    classified_combined[classified_combined["classification"] == "unc mm-Ti"][
                        "classification"].count()
                nonTiNPs = classified_combined[classified_combined["classification"] == "non Ti NPs"][
                    "classification"].count()

                st.code(f"E171:{enp},Rutile:{Rutile},Ilmenite:{Ilmenite}, Biotite:{Biotite}")
                st.code(f"unc sm-Ti:{uncsmNP}, unc mm-Ti:{unclassifiedmmNP}, non Ti NPs:{nonTiNPs}, unclassified:{unclassified}")

                # st.download_button(
                #     label="Download result as csv file",
                #     data=csvresult,
                #     file_name='large_df.csv',
                #     mime='text/csv',
                # )

                labels = ['unclassified','Rutile','Ilmenite','Biotite', 'E171', 'unc sm-Ti', 'unc mm-Ti', 'non Ti Nps']
                sizes = [unclassified, Rutile, Ilmenite, Biotite, enp, uncsmNP, unclassifiedmmNP, nonTiNPs]

                fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, textinfo='label+percent',
                                             insidetextorientation='radial', title='',
                                             )])

                fig

                #######___only__Ti___NP___######
                st.write("Ony Ti containing Nano-Particles")
                enp2 = classified_combined[classified_combined["classification"] == "E171"]["classification"].count()
                Rutile2 = classified_combined[classified_combined["classification"] == "Rutile"][
                    "classification"].count()
                Biotite2 = classified_combined[classified_combined["classification"] == "Biotite"][
                    "classification"].count()
                Ilmenite2 = classified_combined[classified_combined["classification"] == "Ilmenite"][
                    "classification"].count()
                uncsmNP2 = classified_combined[classified_combined["classification"] == "unc sm-Ti"][
                    "classification"].count()
                unclassified2 = classified_combined[classified_combined["classification"] == "unclassified"][
                    "classification"].count()
                unclassifiedmmNP2 = \
                    classified_combined[classified_combined["classification"] == "unc mm-Ti"][
                        "classification"].count()

                st.code(f"E171:{enp2},Rutile:{Rutile2},Ilmenite:{Ilmenite2}, Biotite:{Biotite2}")
                st.code(
                    f"unc sm-Ti:{uncsmNP2}, unc mm-Ti:{unclassifiedmmNP2}, unclassified:{unclassified2}")

                st.download_button(
                    label="Download result",
                    data=csvresult,
                    file_name='large_df.csv',
                    mime='text/csv',
                )

                labels = ['unclassified', 'Rutile', 'Ilmenite', 'Biotite', 'E171', 'sm-Ti', 'unc mm-Ti']
                sizes = [unclassified2, Rutile2, Ilmenite2, Biotite2, enp2, uncsmNP2, unclassifiedmmNP2]
                # PIE chart
                fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, textinfo='label+percent',
                                             insidetextorientation='radial', title='',
                                             )])
                fig

                #####################################
                ############################################

                st.write("Density Heat map")
                mass_cols = (dataframe[['Mg', 'Al', 'Ti',
                                            'V', 'Mn', 'Fe', 'Y',
                                            'Nb', 'La', 'Ce',
                                            'Zr', 'Ta']])
                mass_cols = (dataframe[['Mg', 'Al', 'Ti',
                                            'V', 'Mn', 'Fe','Y',
                                            'Nb', 'La', 'Ce',
                                            'Zr', 'Ta']])
                fig1 = px.imshow(mass_cols, origin='upper', zmin=0,
                                 zmax=10000)

                fig['layout'].update(paper_bgcolor='white', plot_bgcolor='white')
                fig1['layout'].update(plot_bgcolor='#FFFFFF')

                fig.update_layout(plot_bgcolor = "white")
                fig1.update_layout(plot_bgcolor='black')
                fig1.update_layout(width=600, height=400, margin=dict(l=50, r=10, b=30, t=10))
                fig1.update_xaxes(showticklabels=True).update_yaxes(showticklabels=True)
                st.plotly_chart(fig1)

                ###########___Bubble_heatMap_____############
                st.write("Heatmap on sns")
                from matplotlib import pyplot as plt
                import pandas as pd 
                from psynlig import plot_correlation_heatmap

                plt.style.use('default')


                sns.set_theme(context="notebook", style="whitegrid", palette="deep",
                            font="sans-serif", font_scale=1.8,
                            color_codes=True, rc=None)



                selected_cols = (dataframe[['Mg', 'Al', 'Ti',
                                            'V', 'Mn', 'Fe', 'Y',
                                            'Zr', 'Nb', 'La', 'Ce',
                                            'Ta']])
                st.write(selected_cols)
                pd.DataFrame(['selected_cols'])
                kwargs = {
                    'text': {
                        'fontsize': 'large',
                    },
                    'heatmap': {
                        'vmin': -1,
                        'vmax': 1,
                        'cmap':  plt.get_cmap("viridis", 1024)

                    },
                    'figure': {
                        'figsize': (14, 10),


                    },
                }


                corrmap = plot_correlation_heatmap(selected_cols, textcolors=['white', 'black'], bubble=True, annotate=False, **kwargs)
                plt.xticks(rotation=0)
                #plt.yticks(rotation=0)
                plt.savefig("bubble.png")
                plt.show()
                st.image("bubble.png")



            except Exception as ex:
                st.warning(ex)
                # st.warning("Error occured. Could be due to invalid sheet name or corrupted files")

    except Exception as e:
        error = RuntimeError('Error occured while uploading file.')
        st.exception(e)
