# Ti-NP-Classifier
Streamlit program for classification of Ti-ENPs and Ti-NNPs from spICP-TOFMS Data

Steps:
1. Install streamlit, pycharm (or any other IED). Streamlit opens in a browser (for example: google chrome) and the browser acts as graphical user interface. (IED can be used to read or edit codes.)
2. Using Pycharm terminal open streamlit webApp on browser by typing "streamlit run webapp.py" and press enter. Here webapp is the name of the file that contains source codes.
3. Both source code file and helper file should be kept in the same folder.
4. Import all the libraries needed and install the packages.
5. Once you have running webapp, drag or upload the files that you want to classify.
6. A csv or an excel file where mass is defined in attograms can be used for the current program or it can be changed by the user if needed.
7. The user can set the XD_mass (particle-type detection limit in mass) to classify the particles.  For the neat suspension data provided, the X_D,Ti,Ti-Nb value of 9320 ag can be used.  This X_D value is calculated based on a Ti:Nb ratio of 300:1
