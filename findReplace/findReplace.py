import unittest
import os, fnmatch
import re
import sys

levels = {'info': 'info', 'error': 'error', 'warning': 'warn', 'debug': 'debug'}

def replaceLoggingStmts(directory, filePattern):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            classname = filename.replace(".java", "")
            filepath = os.path.join(path, filename)
            if os.access(filepath, os.W_OK):
                print "Working on " + classname +".java"
                # Step 1
                # add logger for each class
                insertloggerstmt = "private static final Logger logger = LoggerFactory.getLogger("+classname+".class);"
                if not insertloggerstmt in open(filepath).read():
                    lineindex = -1
                    declfound = False

                    with open(filepath) as f:
                        data = f.readlines()
                        for line in data:
                            lineindex += 1
                            if "class " + classname in line and not declfound:
                                seq = (line, "\t" + insertloggerstmt, "")
                                line = line.replace(line, "\n".join(seq))
                                declfound = True
                            data[lineindex] = line
                    with open(filepath, "w") as g:
                        g.writelines(data)

                    with open(filepath) as f:
                        s = f.read()

                    # Step 2
                    # change import statements for slf
                    s = __replaceimport(s, classname)

                    # Step 3
                    #replace Log.info/error/warn/fatal(this, ...)
                    #replace Log.infoerror/warn/fatal(xxx.class, ...)
                    s = __replacelogger(s, classname)

                    with open(filepath, "w") as f:
                        f.write(s)

def __replacelogger(s, classname):
    #TODO: handle trace and fatal -- Need change in the logging mode /logger !!!!
    # First pass is to simply use SLF APIs to log
    # Only do not touch Context or any of those core classes
    # Next pass will be to actually replace logger
    # That is when the other details can be looked at

    oldLogger = "Log."
    newLogger = "logger."
    for oldLevel, newLevel in levels.items():
        if oldLevel in ['trace', 'fatal']:
            print classname+".java: Contains trace/fatal logging. Come back to it later."
        s = re.sub(oldLogger + oldLevel + "\s*\(\s*(this|" + classname + ".class)\s*,", newLogger + newLevel + "(", s)
        s = re.sub(oldLogger + oldLevel + "\s*\(", newLogger + newLevel + "(", s)
    return s

def __replaceimport(s, classname):
    return s.replace("import com.abc.util.Log;\n", "import org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;\n")

def __mergetoaline(filepath):
    with open(filepath) as f:
        s = f.read()
        logentries = re.findall('logger(.*?);', s, re.M|re.I|re.DOTALL)
        if logentries:
            # levels = ['info', 'error' , 'warn', 'fatal', 'debug', 'trace']
            for m in logentries:
                if any(level in m for level in levels.values()):
                    m = "logger"+ m +";"
                    s = s.replace(m, m.replace("\n", ""))

    with open(filepath, "w") as f:
        f.write(s)

def __trimwhitespace(filepath):
    lineindex = -1
    with open(filepath) as f:
        data = f.readlines()
        spacepattern = re.compile("\(\s*\"")
        for line in data:
            lineindex += 1
            if "logger." in line:
                line = re.sub(spacepattern, "(\"", line)
            data[lineindex] = line

    with open(filepath, "w") as g:
        g.writelines(data)

def formatLoggingStmts(directory, filePattern):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            filepath = os.path.join(path, filename)
            classname = filename.replace(".java", "")

            if os.access(filepath, os.W_OK):
                #Step 0: Preprocessing

                # 0a. log statement should be in a single line
                # __mergetoaline(filepath)

                # 0b. remove trailing whitespace
                # read line by line and remove space \(\s*"
                __trimwhitespace(filepath)

                #Step 1: Formatting
                # try and format log statements to match slf syntax
                with open(filepath) as f:
                    data = f.readlines()
                    lineindex = -1
                    for line in data:
                        lineindex += 1
                        if "logger." in line:
                            # print line
                            logentry = re.search("\((.*)\)", line)
                            if logentry:
                                m = logentry.group()
                                #print m

                            # format the log stmt correctly and put it back in line
                            # formatted = m
                            # line = line.replace(m, formatted)
                        data[lineindex] = line

                # with open(filepath, "w") as g:
                #     g.writelines(data)

def main(directory):
    replaceLoggingStmts(directory, "*.java")
    formatLoggingStmts(directory, "*.java")


if __name__ == '__main__':
    # unittest.main()
    directory =  sys.argv[1] if len(sys.argv) > 1 else "."
    print directory
    main(directory)






class LoggerReplacerTest(unittest.TestCase):

    def test(self):
        self.assertTrue(True)
