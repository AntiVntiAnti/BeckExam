import datetime
from PyQt6 import QtWidgets
from PyQt6.QtCore import QDate, QSettings, QTime, Qt, QByteArray, QDateTime
from PyQt6.QtGui import QCloseEvent

import tracker_config as tkc
# ////////////////////////////////////////////////////////////////////////////////////////
# UI
# ////////////////////////////////////////////////////////////////////////////////////////
from ui.main_ui.gui import Ui_MainWindow

# ////////////////////////////////////////////////////////////////////////////////////////
# LOGGER
# ////////////////////////////////////////////////////////////////////////////////////////
from logger_setup import logger

# ////////////////////////////////////////////////////////////////////////////////////////
# NAVIGATION
# ////////////////////////////////////////////////////////////////////////////////////////
from navigation.master_navigation import change_stack_page

# Window geometry and frame
from utility.app_operations.frameless_window import (
    FramelessWindow)
from utility.app_operations.window_controls import (
    WindowController)
from utility.app_operations.show_hide import toggle_views
# app ops
# from utility.widgets_set_widgets.slider_spinbox_connections import (
#     connect_slider_spinbox)

# ////////////////////////////////////////////////////////////////////////////////////////
# DATABASE Magicks w/ Wizardry & Necromancy
# ////////////////////////////////////////////////////////////////////////////////////////
# Database connections
from database.database_manager import (
    DataManager)

# Delete Records
from database.database_utility.delete_records import (
    delete_selected_rows)

# setup Models
from database.database_utility.model_setup import (
    create_and_set_model)

# ////////////////////////////////////////////////////////////////////////////////////////
# ADD DATA MODULES
# ////////////////////////////////////////////////////////////////////////////////////////
from database.beck_add_data import add_beck_data


class MainWindow(FramelessWindow, QtWidgets.QMainWindow, Ui_MainWindow):
    """
    The main window of the application.

    This class represents the main window of the application. It inherits from `FramelessWindow`,
    `QtWidgets.QMainWindow`, and `Ui_MainWindow`. It provides methods for handling various actions
    and events related to the main window.

    Attributes:
        becks_model (QAbstractTableModel): The model for the mental mental table.
        ui (Ui_MainWindow): The user interface object for the main window.

    """
    
    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.becks_model = None
        self.ui = Ui_MainWindow()
        self.setupUi(self)
        # Database init
        self.db_manager = DataManager()
        self.setup_models()
        # QSettings settings_manager setup
        self.settings = QSettings(tkc.ORGANIZATION_NAME, tkc.APPLICATION_NAME)
        self.window_controller = WindowController()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.restore_state()
        self.app_operations()
        # self.slider_set_spinbox()
        self.stack_navigation()
        self.delete_group()
        self.set_hidden()
    
        self.update_beck_summary()
        
        #########################################################################
        # beck summer of summation
        #########################################################################
        self.beck_summary.setEnabled(False)
        for slider in [
            self.sadness, self.outlook, self.guilt, self.solitude, self.sexdrive, self.hygiene, self.decisiveness, self.effort, self.interest, self.pessimism, self.victimhood, self.sleep, ]:
            slider.setRange(0, 3)
        
        self.sadness.valueChanged.connect(self.update_beck_summary)
        self.outlook.valueChanged.connect(self.update_beck_summary)
        self.guilt.valueChanged.connect(self.update_beck_summary)
        self.solitude.valueChanged.connect(self.update_beck_summary)
        self.sexdrive.valueChanged.connect(self.update_beck_summary)
        self.hygiene.valueChanged.connect(self.update_beck_summary)
        self.decisiveness.valueChanged.connect(self.update_beck_summary)
        self.effort.valueChanged.connect(self.update_beck_summary)
        self.interest.valueChanged.connect(self.update_beck_summary)
        self.pessimism.valueChanged.connect(self.update_beck_summary)
        self.victimhood.valueChanged.connect(self.update_beck_summary)
        self.sleep.valueChanged.connect(self.update_beck_summary)
    
    def update_beck_summary(self):
        """
        updates the averages of the sliders in the wellbeing and pain module such that
        the overall is the avg of the whole
        :return:
        """
        try:
            
            values = [slider.value() for slider in
                      [self.sadness, self.outlook, self.guilt, self.solitude, self
                      .sexdrive, self.hygiene, self.decisiveness, self.effort, self
                       .interest, self.pessimism, self.victimhood, self.sleep, ] if
                      slider.value() > 0]
            
            sumabitch = sum(values)
            
            self.beck_summary.setValue(int(sumabitch))
        
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
    def set_hidden(self) -> None:
        self.hidemeframe.setVisible(False)
    
    def switch_to_page1(self) -> None:
        """
        Switches to page 1 in the stackedWidget widget and resizes the main window.

        This method sets the current widget of the stackedWidget widget to the page widget,
        and resizes the main window to a width of 400 and a height of 111.

        Returns:
            None
        """
        self.stackedWidget.setCurrentWidget(self.mainpanePage1)
        self.resize(450, 155)
    
    def switch_to_page2(self) -> None:
        """
        Switches to page 2 in the stackedWidget widget and resizes the main window.

        This method sets the current widget of the stackedWidget widget to page_4,
        which represents page 2 in the user interface. It also resizes the main
        window to a width of 800 pixels and a height of 450 pixels.

        Returns:
            None
        """
        self.stackedWidget.setCurrentWidget(self.mainpanePage2)
        self.resize(1000, 450)
    
    def handle_minimize_action(self) -> None:
        """
        Handles the minimize action of the main window.

        Toggles the minimize state of the window using the window controller.

        Raises:
            Exception: If an error occurs while minimizing the window.
        """
        try:
            self.window_controller.toggle_minimize(self)
        except Exception as e:
            logger.exception(f"Error occurred while minimizing {e}", exc_info=True)
    
    def handle_maximize_action(self) -> None:
        """
        Handles the maximize action of the window.

        Toggles the maximize state of the window using the window controller.
        If an error occurs, logs the exception with the error message.

        Raises:
            Exception: If an error occurs while maximizing the window.
        """
        try:
            self.window_controller.toggle_maximize(self)
        except Exception as e:
            logger.exception(f"Error occurred while maximizing {e}", exc_info=True)
    
    # ////////////////////////////////////////////////////////////////////////////////////////
    # APP-OPERATIONS setup
    # ////////////////////////////////////////////////////////////////////////////////////////
    def app_operations(self):
        """
        Performs the necessary operations for setting up the application.

        This method connects signals and slots, sets the initial state of the UI elements,
        and handles various actions triggered by the user.

        Raises:
            Exception: If an error occurs while setting up the app_operations.

        """
        try:
            self.beck_table_commit()
            self.stackedWidget.currentChanged.connect(self.on_page_changed)
            last_index = self.settings.value("lastPageIndex", 0, type=int)
            self.stackedWidget.setCurrentIndex(last_index)
            self.beck_time.setTime(QTime.currentTime())
            self.beck_date.setDate(QDate.currentDate())
            self.actionInput_View.triggered.connect(self.switch_to_page1)
            self.actionDataview.triggered.connect(self.switch_to_page2)
            self.actionMinimize.triggered.connect(self.handle_minimize_action)
            self.actionMaximize.triggered.connect(self.handle_maximize_action)
        except Exception as e:
            logger.error(f"Error occurred while setting up app_operations : {e}", exc_info=True)
    
    def on_page_changed(self, index):
        """
        Callback method triggered when the page is changed in the UI.

        Args:
            index (int): The index of the new page.

        Raises:
            Exception: If an error occurs while setting the last page index.

        """
        try:
            self.settings.setValue("lastPageIndex", index)
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
    
    # ////////////////////////////////////////////////////////////////////////////////////////
    # Minder Navigation
    # ////////////////////////////////////////////////////////////////////////////////////////
    def stack_navigation(self):
        """
        Connects the triggered signals of certain actions to change the stack pages.

        The method creates a dictionary `change_stack_pages` that maps actions to their corresponding page index.
        It then iterates over the dictionary and connects the `triggered` signal of each action to a lambda function
        that calls the `change_stack_page` method with the corresponding page index.

        Raises:
            Exception: If an error occurs during the connection of signals.

        """
        try:
            change_stack_pages = {
                self.actionInput_View: 0,
                self.actionDataview: 1,
            }
            
            for action, page in change_stack_pages.items():
                action.triggered.connect(lambda _, p=page: change_stack_page(self.stackedWidget, p))
        
        except Exception as e:
            logger.error(f"An error has occurred: {e}", exc_info=True)
    
    def beck_table_commit(self) -> None:
        """
        Connects the 'commit' action to the 'add_mentalsolo_data' function and inserts data into the altman_table.

        This method connects the 'commit' action to the 'add_beck_data' function, which inserts data into the beck_table.
        The data to be inserted is retrieved from various UI elements in the main window.

        Raises:
            Exception: If an error occurs during the process.
        """
        try:
            self.actionCommit.triggered.connect(
                lambda: add_beck_data(
                    self, {
                        "beck_date": "beck_date",
                        "beck_time": "beck_time",
                        "sadness": "sadness",
                        "outlook": "outlook",
                        "guilt": "guilt",
                        "solitude": "solitude",
                        "sexdrive": "sexdrive",
                        "hygiene": "hygiene",
                        "decisiveness": "decisiveness",
                        "effort": "effort",
                        "interest": "interest",
                        "pessimism": "pessimism",
                        "victimhood": "victimhood",
                        "sleep": "sleep",
                        "beck_summary": "beck_summary",
                        "model": "becks_model"
                    },
                    self.db_manager.insert_into_beck_table, ))
        except Exception as e:
            logger.error(f"An Error has occurred {e}", exc_info=True)
    
    def delete_group(self):
        """
        Connects the delete action to the delete_selected_rows function.

        This method connects the delete action to the delete_selected_rows function,
        passing the necessary arguments to delete the selected rows in the altman_table.

        Args:
            self: The instance of the main window.

        Returns:
            None
        """
        self.actionDelete_Record.triggered.connect(
            lambda: delete_selected_rows(
                self,
                'beck_tableview',
                'becks_model'
            )
        )
    
    def setup_models(self) -> None:
        """
        Set up the models for the main window.

        This method creates and sets the becks_model using the altman_table.

        Returns:
            None
        """
        self.becks_model = create_and_set_model(
            "beck_table",
            self.beck_tableview
        )
    
    def save_state(self):
        """
        Saves the window geometry state and window state.

        This method saves the current geometry and state of the window
        using the QSettings object. It saves the window geometry state
        and the window state separately.

        Raises:
            Exception: If there is an error saving the window geometry state
                       or the window state.

        """
        try:
            self.settings.setValue("geometry", self.saveGeometry())
        except Exception as e:
            logger.error(f"Error saving the minds_module geo{e}", exc_info=True)
        try:
            self.settings.setValue("windowState", self.saveState())
        except Exception as e:
            logger.error(f"Error saving the minds_module geo{e}", exc_info=True)
    
    def restore_state(self) -> None:
        """
        Restores the window geometry and state.

        This method restores the previous geometry and state of the window
        by retrieving the values from the settings. If an error occurs during
        the restoration process, an error message is logged.

        Raises:
            Exception: If an error occurs while restoring the window geometry or state.
        """
        try:
            # restore window geometry state
            self.restoreGeometry(self.settings.value("geometry", QByteArray()))
        except Exception as e:
            logger.error(f"Error restoring the minds module : stress state {e}")
        
        try:
            self.restoreState(self.settings.value("windowState", QByteArray()))
        except Exception as e:
            logger.error(f"Error restoring WINDOW STATE {e}", exc_info=True)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Event handler for the close event of the window.

        Saves the state before closing the window.

        Args:
            event (QCloseEvent): The close event object.

        Returns:
            None
        """
        try:
            self.save_state()
        except Exception as e:
            logger.error(f"error saving state during closure: {e}", exc_info=True)
