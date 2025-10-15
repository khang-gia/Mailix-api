import datetime
import xlsxwriter

class ExportXlsx():

  wb = None
  ws = None
  current_row = 0

  def __init__(self, output, name) -> None:
    self.current_row = 0
    
    self.wb = xlsxwriter.Workbook(output, {'in_memory': True})
    self.ws = self.wb.add_worksheet(name)
    
  def add_header(self, columns):
    bold = self.wb.add_format({'bold': True})
    for num, value in enumerate(columns):
      self.ws.write(self.current_row, num, value, bold)
  
  def add_row(self, columns):
    self.current_row = self.current_row + 1
    date_format = self.wb.add_format({'num_format': 'dd/mm/yyyy'})
    datetime_format = self.wb.add_format({'num_format': 'dd/mm/yyyy hh:MM'})
    for y, value in enumerate(columns):
      if isinstance(value, datetime.date):
        self.ws.write(self.current_row, y, value, date_format)
      elif isinstance(value, datetime.datetime):
        self.ws.write(self.current_row, y, value, datetime_format)
      else:
        self.ws.write(self.current_row, y, value)

  def close(self):
    self.wb.close()

    