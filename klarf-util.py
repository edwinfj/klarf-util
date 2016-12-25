#!/usr/local/bin/python3.5
# default python3.5
import numpy as np

def read_attr_from_klarf(klarf, atrr='CLASSNUMBER'):
  """
  read attribute from a klarf file

  INPUT
  - klarf: path to the klarf file to be read
  - attr: attribute that you want to read. default 'CLASSNUMBER'
  OUTPUT
  - IDs: a list containing IDs of all defects in the klarf;
  - attr_values: a list containing values of attr of all defects in the klarf, 
    attr_values[i] is attr value of IDs[i]; 
  """
  with open(klarf, 'r') as f:
    line = f.readline()
    if '1.8' in line:
      IDs, attr_values = klarf_parse_1_8(f, lreal, lfalse)
    elif '2' in line:
      IDs, attr_values = klarf_parse_1_2(f, lreal, lfalse)

  return IDs, attr_values

def klarf_parse_1_8(kf, attr='CLASSNUMBER'):
  """
  parse 1.8 version klarf

  INPUT
  - kf: file stream opened for a klarf file
  - attr: attribute that you want to read. default 'CLASSNUMBER'
  OUTPUT
  - IDs: a list containing IDs of all defects in the klarf;
  - attr_values: a list containing values of attr of all defects in the klarf, 
    attr_values[i] is attr value of IDs[i]; 
  """
  # find the header "List DefectList"
  for line in kf:
    if 'DefectList' in line:
      break
  kf.readline() # escape the '{'
  cc_idx = 0 # identify which column is attr
  search_flag = True # search for the index of attr when True
  for line in kf:
    if search_flag and attr in line:
      t = line.split(',')
      for word in t:
        if attr in word:
          search_flag = False # found, no need search anymore
          break
        else:
          cc_idx += 1
    elif search_flag:
      cc_idx += len(line.split(',')) - 1 # each line is trailing with ','

    if '}' in line: # reached the end of attribute list
      break
  # now reached the 'Data xxxxx' line
  kf.readline()
  kf.readline()
  IDs, attr_values = [], []
  word_count = 0
  for line in kf:
    if '}' in line: # end of all defects
      break
    words = line.split()
    if word_count == 0: # beginning of a defect attributes
      ID = int(words[0])
    len_words = len(words)
    if len_words + word_count > cc_idx >= word_count:
      IDs.append(ID)
      attr_values.append(int(words[cc_idx - word_count]))

    word_count += len_words
    if ';' in line: # end of a defect attributes
      word_count =0

  return IDs, attr_values

def klarf_parse_1_2(kf, attr='CLASSNUMBER'):
  """
  parse 1.2 version klarf

  INPUT
  - kf: file stream opened for a klarf file
  - attr: attribute that you want to read. default 'CLASSNUMBER'
  OUTPUT
  - IDs: a list containing IDs of all defects in the klarf;
  - attr_values: a list containing values of attr of all defects in the klarf, 
    attr_values[i] is attr value of IDs[i]; 
  """
  # find the header "List DefectList"
  for line in kf:
    if 'DefectRecordSpec' in line:
      break
  words = line.split()
  for i in range(len(words)):
    if words[i] == attr:
      cc_idx = i - 2
      break
  kf.readline() # escape 'DefectList' line
  IDs, attr_values = [], []
  for line in kf:
    words = line.split()
    IDs.append(int(words[0]))
    attr_values.append(int(words[cc_idx]))
    if ';' in line:
      break

  return IDs, attr_values

def write_attr_to_klarf(template, IDs, attr_values, target, 
                          attr='FINEBINNUMBER'):
  """
  write attribute values to corresponding defects in a template klarf file and 
  save as a new klarf

  INPUT
  - template: path to the template klarf file to be read from
  - IDs: int, list containing defect IDs for changing class codes
  - attr_values: list containing attribute values, IDs[i] correspond to 
    attr_values[i]
  - target: path to the target klarf file to be written to
  - attr: name of the attribute that write values to, default 'FINEBINNUMBER'
  """
  # convert IDs - attr_values to dictionary representation
  defects = {}
  defects.update(zip(IDs, attr_values))

  with open(template, 'r') as fread, open(target, 'w') as fwrite:
    line = fread.readline()
    fwrite.write(line)
    if '1.8' in line:
      klarf_modify_1_8(fread, defects, fwrite, attr)
    elif '2' in line:
      klarf_modify_1_2(fread, defects, fwrite, attr)

def klarf_modify_1_8(fread, defects, fwrite, attr='FINEBINNUMBER'):
  """
  write attribute values to corresponding defects in a template 1.8 version 
  klarf file and save as a new klarf

  INPUT
  - fread: file stream to the template klarf
  - defects: dictionary {defect_ID: attr_value} containing defects to update 
    attr
  - fwrite: file stream to the target file
  - attr: name of the attribute that write values to, default 'FINEBINNUMBER'
  """
  # find the header "List DefectList"
  for line in fread:
    fwrite.write(line)
    if 'DefectList' in line:
      break
  fwrite.write(fread.readline()) # escape the '{'
  cc_idx = 0 # identify which column is attr
  search_flag = True # search for the index of attr when True
  for line in fread:
    fwrite.write(line)
    if search_flag and attr in line:
      t = line.split(',')
      for word in t:
        if attr in word:
          search_flag = False # found, no need search anymore
          break
        else:
          cc_idx += 1
    elif search_flag:
      cc_idx += len(line.split(',')) - 1 # each line is trailing with ','
    if '}' in line: # reached the end of attribute list
      break
  # now reached the 'Data xxxxx' line
  fwrite.write(fread.readline())
  fwrite.write(fread.readline())
  word_count = 0
  for line in fread:
    if '}' in line: # end of all defects
      fwrite.write(line)
      break
    words = line.split()
    if word_count == 0: # beginning of a defect attributes
      ID = int(words[0]) # retreive the ID of current defect
    len_words = len(words)
    if len_words + word_count > cc_idx >= word_count and ID in defects:
      words[cc_idx - word_count] = str(defects[ID])
      fwrite.write(' '*12 + ' '.join(words) + ' \n')
    else:
      fwrite.write(line)
    word_count += len_words
    if ';' in line: # end of a defect attributes
      word_count =0
  # write the rest lines to new klarf
  for line in fread:
    fwrite.write(line)

def klarf_modify_1_2(fread, defects, fwrite, attr='FINEBINNUMBER'):
  """
  write attribute values to corresponding defects in a template 1.2 version 
  klarf file and save as a new klarf

  INPUT
  - fread: file stream to the template klarf
  - defects: dictionary {defect_ID: attr_values} containing defects to update 
    attr
  - fwrite: file stream to the target file
  - attr: name of the attribute that write values to, default 'FINEBINNUMBER'
  """
  # find the header "List DefectList"
  for line in fread:
    fwrite.write(line)
    if 'DefectRecordSpec' in line:
      break
  words = line.split()
  for i in range(len(words)):
    if words[i] == attr:
      cc_idx = i - 2
      break
  fwrite.write(fread.readline()) # escape 'DefectList' line
  for line in fread:
    words = line.split()
    ID = int(words[0])
    if ID in defects:
      words[cc_idx] = str(defects[ID])
      fwrite.write(' ' + ' '.join(words) + '\n')
    else:
      fwrite.write(line)
    if ';' in line:
      break
  # write the rest of lines to new klarf
  for line in fread:
    fwrite.write(line)

if __name__ == '__main__':
  import sys
  argc = len(sys.argv)

  # test read_attr_from_klarf()
  # if argc < 2:
  #   raise ValueError('no klarf file specified')
  #   exit()
  # elif argc == 2:
  #   klarf = sys.argv[1]
  #   lreal = []
  #   lfalse = []
  # elif argc == 3:
  #   klarf = sys.argv[1]
  #   lreal = [int(i) for i in (sys.argv[2])[1:-1].split(',')]
  #   lfalse = []
  # elif argc == 4:
  #   klarf = sys.argv[1]
  #   lreal = [int(i) for i in (sys.argv[2])[1:-1].split(',')]
  #   lfalse = [int(i) for i in (sys.argv[3])[1:-1].split(',')]
  # else:
  #   raise ValueError('unkown parameters %s ...' % (argv[4],))

  # IDs, attr_values = read_attr_from_klarf(klarf, lreal, lfalse)
  # with open('../test', 'w') as f:
  #   for ID, cc in zip(IDs, attr_values):
  #     f.write('%d, %d\n' % (ID, cc))

  # test write_attr_to_klarf()
  IDs = [58324, 58326, 58331, 58333]
  ccs = [999, 998, 997, 996]
  if argc != 3:
    raise ValueError('incorrect arguments. Only need template klarf, and target')
  else:
    write_attr_to_klarf(sys.argv[1], IDs, ccs, sys.argv[2], 'FINEBINNUMBER')