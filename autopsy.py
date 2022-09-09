import os
import threading

from time import time

from urllib2 import urlopen
from contextlib import closing

from shutil import copyfileobj

from java.util import UUID
from java.awt import Dimension
from java.awt import Component
from javax.swing import JPanel
from javax.swing import JTextField
from javax.swing import BoxLayout
from javax.swing import JLabel
from javax.swing.border import EmptyBorder
from java.beans import PropertyChangeSupport

from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.corecomponentinterfaces import DataSourceProcessor
from org.sleuthkit.autopsy.corecomponentinterfaces import DataSourceProcessorCallback
from org.sleuthkit.autopsy.datasourceprocessors import DataSourceProcessorAdapter  
from org.sleuthkit.autopsy.casemodule.services.FileManager import FileAddProgressUpdater

# https://www.sleuthkit.org/autopsy/docs/api-docs/4.17.0/_raw_d_s_processor_8java_source.html
# https://www.sleuthkit.org/autopsy/docs/api-docs/4.19.3/_raw_d_s_processor_8java_source.html

class RemoteCaseProcessor(DataSourceProcessorAdapter):
    configPanel = None
    moduleName = "Remote Case Generator"

    def __init__(self):
        self.configPanel = DataSourcesPanelSettings()
    
    @staticmethod
    def getType():
        return RemoteCaseProcessor.moduleName

    def getDataSourceType(self):
        return self.moduleName

    def getPanel(self):
        return self.configPanel

    def isPanelValid(self):
        return self.configPanel.validatePanel()

    def run(self, host, progressMonitor, callback):
        self.configPanel.run(host, progressMonitor, callback)

    #Overrides not used
    def cancel(self):
        pass

    #Overrides not used
    def reset(self):
        pass

class ProgressUpdater(FileAddProgressUpdater):
    def __init__(self):
        self.files = []
        pass
    
    def fileAdded(self, newfile):
        self.files.append(newfile)
        
    def getFiles(self):
        return self.files

class ModuleUtils:
    @staticmethod
    def add_to_fileset(name, folder, device_id = UUID.randomUUID(), progress_updater = ProgressUpdater(), notify = True):
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        skcase_data = Case.getCurrentCase()
        
        data_source = fileManager.addLocalFilesDataSource(device_id.toString(), name, "", folder, progress_updater)
        
        if notify:
            files_added = progress_updater.getFiles()
            for file_added in files_added:
                skcase_data.notifyDataSourceAdded(file_added, device_id)

        return data_source

class DataSourcesPanelSettings(JPanel):
    serialVersionUID = 1

    def __init__(self):
        self.pcs = PropertyChangeSupport(self)
        self.link_url = ""
        self.initComponents()

    def getVersionNumber(self):
        return serialVersionUID

    #PROCESSOR LOGIC
    def run(self, host, progressMonitor, callback):
        threading.Thread(target=self.running, args=[progressMonitor, callback]).start()

    def running(self, progressMonitor, callback):
        result = DataSourceProcessorCallback.DataSourceProcessorResult.NO_ERRORS
        progressMonitor.setIndeterminate(True)
        data_sources = []
        errors = []

        progressMonitor.setProgressText('\tDownloading contents from {}\n\tPlease wait.'.format(self.link_url))
        artefact_path = os.path.join(Case.getCurrentCase().getTempDirectory(), "remote_case")
        if not os.path.exists(artefact_path):
            os.makedirs(artefact_path)

        download_path = os.path.join(artefact_path, 'file.zip')
        # download_path = os.path.join('/home/myuser/aut/test', 'file.zip')

        try: 
            downloader = Downloader(self.link_url, download_path)
            downloader.download()
            data_sources.append(ModuleUtils.add_to_fileset('RemoteCase{} - {}'.format(int(time()), self.link_url), [download_path]))
            
        except Exception as e:
            message = "Downloader Failed. Aborting: {}".format(e)
            errors.append(message)
            result = DataSourceProcessorCallback.DataSourceProcessorResult.CRITICAL_ERRORS


        callback.done(result, errors, data_sources)

    # def addPropertyChangeListener(self, pcl):
    #     super(DataSourcesPanelSettings, self).addPropertyChangeListener(pcl)
    #     self.pcs.addPropertyChangeListener(pcl)

    def fireUIUpdate(self):
        #Fire UI change, this is necessary to know if it's allowed to click next
        self.pcs.firePropertyChange(DataSourceProcessor.DSP_PANEL_EVENT.UPDATE_UI.toString(), False, True);        

    def validatePanel(self):
        return self.link_url != ""

    def initComponents(self):
        self.link_url = "https://sample-videos.com/zip/10mb.zip"

        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))
        self.setPreferredSize(Dimension(543, 172)) #Max 544x173 https://www.sleuthkit.org/autopsy/docs/api-docs/3.1/interfaceorg_1_1sleuthkit_1_1autopsy_1_1corecomponentinterfaces_1_1_data_source_processor.html#a068919818c017ee953180cc79cc68c80
        
        # info menu
        self.p_info = self.createPanel()
        self.p_info.setPreferredSize(Dimension(543,172))
        self.d_method = self.createPanel(pbottom = 15)

        self.label = JLabel('Introduce the URL of the ZIP file containing the data to be analyzed.')
        self.label.setBorder(EmptyBorder(0,0,5,0))

        self.d_method.add(self.label)

        self.text_field = JTextField(8)
        self.text_field.setText(self.link_url)
        self.d_method.add(self.text_field)

        self.add(self.d_method)
        self.add(self.p_info)

    def createPanel(self, scroll = False, ptop = 0, pleft = 0, pbottom = 0, pright = 0):
        panel = JPanel()
        panel.setLayout(BoxLayout(panel, BoxLayout.PAGE_AXIS))
        panel.setAlignmentX(Component.LEFT_ALIGNMENT)
        panel.setBorder(EmptyBorder(ptop, pleft, pbottom, pright))
        
        # if scroll:
            # scrollpane = JScrollPane(panel)
            # scrollpane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
            # scrollpane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_NEVER)
            # return JPanel().add(scrollpane)
        
        return panel

class Downloader:
    def __init__(self, url, path):
        self.url = url
        self.path = path

    def download(self):
        with closing(urlopen(self.url)) as response, open(self.path, 'wb') as out_file:
            copyfileobj(response, out_file)