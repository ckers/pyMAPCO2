"""
Created on Jul 29, 2013
@author: Colin Dietrich

Utility classes and methods for various tasks

TODO: break in to modules so imports don't require unused modules

"""

import random
import os
import time
import threading
import queue
import itertools

from os import listdir
from os.path import isfile, join

from matplotlib.pyplot import get_cmap

import tkinter
import tkinter.filedialog as tkfd


mpl_styles = ["-",     # solid line style
             "--",   # dashed line style
             "-.",   # dash-dot line style
             ":"]    # dotted line style

mpl_markers = [".",    # point marker
             ",",    # pixel marker
             "o",    # circle marker
             "v",    # triangle_down marker
             "^",    # triangle_up marker
             "<",    # triangle_left marker
             ">",    # triangle_right marker
             "1",    # tri_down marker
             "2",    # tri_up marker
             "3",    # tri_left marker
             "4",    # tri_right marker
             "s",    # square marker
             "p",    # pentagon marker
             "*",    # star marker
             "h",    # hexagon1 marker
             "H",    # hexagon2 marker
             "+",    # plus marker
             "x",    # x marker
             "D",    # diamond marker
             "d",    # thin_diamond marker
             "|",    # vline marker
             "_"]    # hline marker

mpl_markers_obvious = ["o",    # circle marker
             "v",    # triangle_down marker
             "^",    # triangle_up marker
             "<",    # triangle_left marker
             ">",    # triangle_right marker
             "s",    # square marker
             "p",    # pentagon marker
             "*",    # star marker
             "h",    # hexagon1 marker
             "H",    # hexagon2 marker
             "D",    # diamond marker
             "d"]#,    # thin_diamond marker
#             "|",    # vline marker
#             "_"]    # hline marker

class Timer(object):
    """Provides a timer in seconds
    """
    def __init__(self, name=None):
        self.name = name
    
    def __enter__(self):
        self.tstart = time.time()
        
#    def __exit__(self, type, value, traceback):
    def __exit__(self):
        if self.name:
            print('[%s]' % (self.name))
        print('Elapsed: %s' % (time.time() - self.tstart))

class Bunch:
    """Group dictionary items into Class attributes"""

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    # that's it!  Now, you can create a Bunch
    # whenever you want to group a few variables:

    # >>> point = Bunch(datum=y, squared=y*y, coord=x)

    # and of course you can read/write the named
    # attributes you just created, add others, del
    # some of them, etc, etc:
    # >>> if point.squared > threshold:
    # >>>     point.isok = 1

    
def binseq(k):
    """Create an list of all binary permutations of a certain length
    Note: for very large k, this could max RAM usage.
    """
    return [''.join(x) for x in itertools.product('01', repeat=k)]

def get_all_from_queue(Q):
    """ Generator to yield one after the others all items 
        currently in the queue Q, without any waiting.
    """
    try:
        while True:
            yield Q.get_nowait( )
    except queue.Empty:
        raise StopIteration


def get_item_from_queue(Q, timeout=0.01):
    """ Attempts to retrieve an item from the queue Q. If Q is
        empty, None is returned.
        
        Blocks for 'timeout' seconds in case the queue is empty,
        so don't use this method for speedy retrieval of multiple
        items (use get_all_from_queue for that).
    """
    try: 
        item = Q.get(True, 0.01)
    except queue.Empty: 
        return None
    
    return item


def flatten(iterables):
    """ Flatten an iterable of iterables. Returns a generator.
        
        list(flatten([[2, 3], [5, 6]])) => [2, 3, 5, 6]
    """
    return (elem for iterable in iterables for elem in iterable)


def argmin_list(seq, func):
    """ Return a list of elements of seq[i] with the lowest 
        func(seq[i]) scores.
        >>> argmin_list(['one', 'to', 'three', 'or'], len)
        ['to', 'or']
    """
    best_score, best = func(seq[0]), []
    for x in seq:
        x_score = func(x)
        if x_score < best_score:
            best, best_score = [x], x_score
        elif x_score == best_score:
            best.append(x)
    return best


def argmin_random_tie(seq, func):
    """ Return an element with lowest func(seq[i]) score; break 
        ties at random.
    """
    return random.choice(argmin_list(seq, func))


def argmin(seq, func):
    """ Return an element with lowest func(seq[i]) score; tie goes 
        to first one.
        >>> argmin(['one', 'to', 'three'], len)
        'to'
    """
    return min(seq, key=func)


def argmax_list(seq, func):
    """ Return a list of elements of seq[i] with the highest 
        func(seq[i]) scores.
        >>> argmax_list(['one', 'three', 'seven'], len)
        ['three', 'seven']
    """
    return argmin_list(seq, lambda x: -func(x))


def argmax_random_tie(seq, func):
    """ Return an element with highest func(seq[i]) score; break 
        ties at random.
    """
    return random.choice(argmax_list(seq, func))


def argmax(seq, func):
    """ Return an element with highest func(seq[i]) score; tie 
        goes to first one.
        >>> argmax(['one', 'to', 'three'], len)
        'three'
    """
    return max(seq, key=func)

def sort_directory(directory):
    """Get a list of files in a directory and sort them alpha-numerically.
    
    Parameters
    ----------
    directory : string, absolute path of directory containing more than 
                one data set.
    
    Returns
    -------
    sorted_files : list, absolute paths to all files in directory.
    
    Notes
    -----
    If files are not zero padded, sort_lj_data will pad them; otherwise
    the files in directory will just be sorted and returned.
    """
    
    # parse the default archive directory set in the config file
    file_list, dir_list = file_ops.walk_dir(directory) #@UnusedVariable
    
    if file_list == False:
        return(False)
    
    # sort it alpha-numerically
    file_list.sort()
    
    return(file_list)
    
def color_generator(NUM_COLORS):
    """create a list of colors for matplotlib plotting
    Inputs:    n, int, number of colors to generate
    
    Results:    colors, list, 
    """
    # from matplotlib.pyplot
    cm = get_cmap('gist_rainbow')
    colors = [cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]
    return colors
    
def concurrent_map(func, data):
    """
    Similar to the bultin function map(). But spawn a thread for each argument
    and apply `func` concurrently.

    Note: unlike map(), we cannot take an iterable argument. `data` should be an
    indexable sequence.
    """
    
    N = len(data)
    result = [None] * N
    
    lock = threading.Lock()
    # wrapper to dispose the result in the right slot
    def task_wrapper(i):
        lock.acquire()
        result[i] = func(data[i])
        lock.release()
        
    threads = [threading.Thread(target=task_wrapper, args=(i,)) for i in range(N)]
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    return result

def dir_dialog(initial=False, title='Please select a directory'):
    """Convenience wrapper for tkfd.askdirectory, gives user a window
    to select a directory.
    
    Parameters
    ----------
    initial : string, initial directory to open selection dialog in
    title : string, title to display in selection dialog
    
    Returns
    -------
    d_name : string, full path to directory as selected by the user
    """

    if (initial is False) or (os.path.exists(initial) is False):
        initial = os.path.dirname(os.path.realpath(__file__))

    root = tkinter.Tk()
    root.withdraw()

    try:
        d_name = tkfd.askdirectory(parent=root,
                                   initialdir=os.path.normpath(initial),
                                   title=title)
        if len(d_name) > 0:

            return d_name
        else:
            return False
    except:
        return False


def file_dialog(initial=False, title='Choose a file'):
    """Convenience wrapper for tkfd.askopenfilename, 
    gives user a window to select a file.
    
    Parameters
    ----------
    initial : string, initial directory to open selection dialog in
    title : string, title to display in selection dialog
    
    Returns
    -------
    f_name : string, full path to file as selected by the user
    """

    if initial == False or os.path.exists(initial) == False:
        initial = os.path.dirname(os.path.realpath(__file__))

    root = tkinter.Tk()
    root.withdraw()

    try:
        f_name = tkfd.askopenfilename(parent=root,
                                      initialdir=os.path.normpath(initial),
                                      title=title)
        if f_name:
            return (f_name)
        else:
            return (False)
    except:
        return (False)


def save_dialog(initial=False):
    """Convenience wrapper for tkfd.asksaveasfilename, 
    gives user a window to save a file.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    f_name : string, full path to file as selected by the user
    """

    myFormats = [
        ('Windows Bitmap', '*.bmp'),
        ('Portable Network Graphics', '*.png'),
        ('JPEG / JFIF', '*.jpg'),
        ('CompuServer GIF', '*.gif'),
    ]

    if initial == False:
        initial = os.path.dirname(os.path.realpath(__file__))

    root = tkinter.Tk()
    root.withdraw()

    try:
        f_name = tkfd.asksaveasfilename(parent=root,
                                        filetypes=myFormats,
                                        title="Save the image as...")

        if len(f_name) > 0 and f_name != None:
            return (f_name)
        else:
            return (False)
    except:
        return (False)


def n_files(n):
    files = []
    for i in range(0, n):
        files.append(file_dialog(t='Choose file %s' % str(int(i) + 1)))
    return (files)


def walk_dir(root_folder):
    """Walks through a directory and compiles a numpy array of the data.
    
    Parameters:
    root_folder : string
        absolute path to archive
        
    Returns:
    full_file_list : List of absolute paths to all files in directory
    full_dir_list :  List of absolute paths to all directories in directory
    """

    # find out if the path uses forward or backward slashes
    # s.find() returns -1 if character not found, otherwise character count
    # rf = str(root_folder)
    # if rf.find('\\') > rf.find('/'):
    #    separator = '\\'
    # else: separator = '/'
    root_folder = os.path.normpath(root_folder)

    try:
        # walk through the directory and find all the files and directories
        root_folder, directories, file_list = os.walk(root_folder).next()
    except:
        return (False, "Unable to walk directory")

    # sorting gets the file list in chronological order
    file_list.sort()

    # new list for full filepath names
    full_file_list = []
    full_dir_list = []

    # walk through each file
    for one_file in file_list:
        full_file_list.append(os.path.normpath(root_folder + "/" + one_file))

    # walk through each folder
    for one_folder in directories:
        full_dir_list.append(os.path.normpath(root_folder + "/" + one_folder))

    return (full_file_list, full_dir_list)


def target(path_target, timestamp=False, description='generic'):
    """Create a valid .csv file name and path to save it.  Note that
    in Unix systems and MS Windows, the path_target is the sole
    portion of the file path that utilizes '/' or '\' characters.
    The path_target input must be correct for the OS, or checked elsewhere.
    """

    if timestamp == False:
        timestamp = time.strftime('%Y_%m_%d_%H_%M_%S')

    try:
        d = str(description)
        path_filename = os.path.normpath(path_target + d + '_' + timestamp + '.csv')
        return (path_filename)
    except:
        return (False, 'Problem loading save file target')


def record(path_filename, data):
    """Write data to file at the specified location.  open() will make the file 
    if the called file does not exist - no need to check time or file creation
    """
    try:
        f = open(os.path.normpath(path_filename), 'a')
        data = str(data)
        f.write(data)
        f.close()
        return ('Record saved with record successfully')
    except:
        return (False)


def read_file(path_filename, lines_to_read):
    """Read specified lines from a file.
    
    Parameters
    ----------
    path_filename : string, absolute path to file to open
    rows    : list of integers, row numbers to read data from
    
    Returns
    -------
    line_list :    list of strings, value of lines contained within range
                    given by rows
    """
    with open(path_filename, 'r') as f:
        return ([s for s in read_specific_lines(f, lines_to_read)])


def read_specific_lines(path_filename, lines_to_read):
    """file is any iterable; lines_to_read is an iterable containing int values"""
    lines = set(lines_to_read)
    last = max(lines)
    for n, line in enumerate(path_filename):
        if n in lines:
            yield line
        if n > last:
            return


def record_log(data_type, data):
    """Accepts a string for the data type (stream, tjson, anything)
    and a line of tweet data that produced an error.  Type will 
    be added to log filename, as in 'date - type log.txt'"""
    today = time.strftime("20%y_%m_%d")
    path_filename = results_filepath + today + " - " + str(data_type) + " log.txt"
    now = time.strftime("20%y_%m_%d - %H_%M_%S,")
    record(path_filename, now + str(data))


def complex_line_record(path_filename, data):
    path_filename = os.path.normpath(path_filename)
    l = []
    for n in range(0, len(data)):
        imaginary = data[n].imag
        if imaginary < 0:
            sign = "-"
        else:
            sign = "+"
        x = "%.14f%s%.14fj" % (data[n].real, sign, abs(imaginary))
        l.append(x)
    s = ",".join(l)
    s = s + "\n"
    record(path_filename, s)


def complex_line_record_excel(path_filename, data):
    path_filename = os.path.normpath(path_filename)
    l = []
    for n in range(0, len(data)):
        imaginary = data[n].imag
        if imaginary < 0:
            sign = "-"
        else:
            sign = "+"
        x = "$$COMPLEX(%.14f,%s%.14f)" % (data[n].real, sign, abs(imaginary))
        l.append(x)
    s = "\t".join(l)
    s = s + "\n"
    record(path_filename, s)


def real_line_record(path_filename, data):
    path_filename = os.path.normpath(path_filename)
    l = []
    for n in range(0, len(data)):
        x = "%.14f,%.14f" % (data[n].real, data[n].imag)
        l.append(x)
    s = ",".join(l)
    s = s + "\n"
    record(path_filename, s)


def make_folder(self, parent_folder, timestamp=False, suffix=False):
    if timestamp == False:
        timestamp = time.strftime('%Y_%m_%d_%H_%M_%S')

    if suffix == False or '':
        folder_and_suffix = timestamp
    else:
        folder_and_suffix = timestamp + ' - ' + suffix

    dir_path = os.path.normpath(parent_folder + "/" + folder_and_suffix + "/")

    # mkdir from the os library
    os.mkdir(dir_path)

    return (dir_path)


def sort_directory(directory):
    """Get a list of files in a directory and sort them alpha-numerically.
    
    Parameters
    ----------
    directory : string, absolute path of directory containing more than 
                one data set.
    
    Returns
    -------
    sorted_files : list, absolute paths to all files in directory.
    
    Notes
    -----
    If files are not zero padded, sort_lj_data will pad them; otherwise
    the files in directory will just be sorted and returned.
    """

    # parse the default archive directory set in the config file
    file_list, dir_list = walk_dir(directory)  # @UnusedVariable

    if not file_list:
        return False

    # sort it alpha-numerically
    file_list.sort()

    return file_list


def files_in_directory(directory_path, hint, skip=None):
    """Find all files a certain file extension in a directory.
    Checks for skip string only after it has matched the hint.

    Parameters
    ----------
    directory_path : str, path to directory
    hint : str, string in filename to look for
    skip : str, string in filename to skip

    Returns
    -------
    list, of str containing file names matching hint and excluding skip
    """

    files = [f for f in os.listdir(directory_path)
             if os.path.isfile(os.path.join(directory_path, f)) &
             (hint in f)]

    if skip is not None:
        files = [f for f in files if skip not in f]

    return files


def pad_date(date):
    """Zero pad a date, delimited with '/'
    Assumes year is index 2.
    """
    
    a = date.split('/')
    g = ['00', '00', '0000']
    for x in range(0,3):
        if len(a[x]) == 1:
            g[x] = '0' + a[x]
        else:
            g[x] = a[x]
        if x == 2 and len(a[x]) == 2:
            g[x] = '20' + a[x]
    g = '/'.join(g)
    return g

