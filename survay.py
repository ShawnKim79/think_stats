import sys
import gzip
import os

class Record(object):
    """Represents a record."""

class Respondent(Record): 
    """Represents a respondent."""

class Pregnancy(Record):
    """Represents a pregnancy."""

class Table(object):
    def __init__(self):
        self.records = []
    def __len__(self):
        return len(self.records)
    def ReadFile(self, data_dir, filename, fields, constructor, n=None):
        filename = os.path.join(data_dir, filename)
        if filename.endswith('gz'):
            fp = gzip.open(filename)
        else:
            fp = open(filename)

        for i, line in enumerate(fp):
            if i == n:
                break
            record = self.MakeRecord(line, fields, constructor)
            self.AddRecord(record)
        fp.close()

    def MakeRecord(self, line, fields, constructor):
        obj = constructor()
        for (field, start, end, cast) in fields:
            try:
                s = line[start-1:end]
                val = cast(s)
            except ValueError:
                val = 'NA'
            setattr(obj, field, val)
        return obj

    def AddRecord(self, record):
        self.records.append(record)

    def ExtendRecords(self, records):
        self.records.extend(records)

    def Recode(self):
        pass


class Respondents(Table):
    def ReadRecords(self, data_dir='.', n=None):
        filename = self.GetFilename()
        self.ReadFile(data_dir, filename, self.GetFields(), Respondent, n)
        self.Recode()

    def GetFilename(self):
        return '2002FemResp.dat.gz'

    def GetFields(self):
        return [
            ('caseid', 1, 12, int),
            ]

class Pregnancies(Table):
    """Contains survey data about a Pregnancy."""

    def ReadRecords(self, data_dir='.', n=None):
        filename = self.GetFilename()
        self.ReadFile(data_dir, filename, self.GetFields(), Pregnancy, n)
        self.Recode()

    def GetFilename(self):
        return '2002FemPreg.dat.gz'

    def GetFields(self):
        return [
            ('caseid', 1, 12, int),
            ('nbrnaliv', 22, 22, int),
            ('babysex', 56, 56, int),
            ('birthwgt_lb', 57, 58, int),
            ('birthwgt_oz', 59, 60, int),
            ('prglength', 275, 276, int),
            ('outcome', 277, 277, int),
            ('birthord', 278, 279, int), #정상출산 : 1
            ('agepreg', 284, 287, int),
            ('finalwgt', 423, 440, float),
        ]

    def Recode(self):
        for rec in self.records:
            try:
                if rec.agepreg != 'NA':
                    rec.agepreg /= 100.0
            except AttributeError:
                pass
            try:
                if (rec.birthwgt_lb != 'NA' and rec.birthwgt_lb < 20 and
                    rec.birthwgt_oz != 'NA' and rec.birthwgt_oz <= 16):
                    rec.totalwgt_oz = rec.birthwgt_lb * 16 + rec.birthwgt_oz
                else:
                    rec.totalwgt_oz = 'NA'
            except AttributeError:
                pass
    
    def BirthordCount(self, data_dir='.', n=None):
        filename = self.GetFilename()
        self.ReadFile(data_dir, filename, self.GetFields(), Pregnancy, n)
        return self.BirthordRecode()
    
    def BirthordRecode(self):
        birthord = 0
        for rec in self.records:
            try:
                if rec.birthord == 1:
                    birthord += 1
            except AttributeError:
                pass
        return birthord


def main(name, data_dir='.'):
    resp = Respondents()
    resp.ReadRecords(data_dir)
    print ('Number of respondents :', len(resp.records))

    preg = Pregnancies()
    preg.ReadRecords(data_dir)
    print ('Number of pregnancies :', len(preg.records))
    
    print ('birthord count :', preg.BirthordCount(data_dir))   

    
if __name__ == '__main__':
    main(*sys.argv)