from qtpy import QtWidgets, QtGui, QtCore, uic
import traceback
import sys
import os

class ProgressDialog(QtWidgets.QDialog):

    def __init__(self, text, min, max, threadpool, mainwindow):
        super(ProgressDialog, self).__init__()
        self.setModal(True)
        self.threadpool = threadpool
        self.min = min
        self.max = max
        self.count = min
        self.mainwindow = mainwindow
        source_update_ui = os.path.join(self.mainwindow.basedir, 'data/progress_dialog.ui')
        uic.loadUi(source_update_ui, self)
        self.label.setText(str(text))
        self.progressBar.setMinimum(self.min)
        self.progressBar.setMaximum(self.max)
        self.progressBar.setValue(self.count)
        self.pushButtonCancel.clicked.connect(self.cancel)
        self.show()

    def increment(self):
        self.count += 1
        self.progressBar.setValue(self.count)
        if self.count >= self.max:
            self.close()

    def cancel(self):
        self.threadpool.clear()
        self.close()

class WorkerSignals(QtCore.QObject):

    finished = QtCore.Signal()
    error = QtCore.Signal(tuple)
    result = QtCore.Signal(object)
    progress = QtCore.Signal(int)


class Worker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the progress callback to our kwargs IF the func has a "progress_callback" parameter
        if 'progress_callback' in self.fn.__code__.co_varnames:
            self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

