import re


class UnicalAttributeProcessor:
    @staticmethod
    def codice_fiscale_rs(schacpersonaluniqueids=[], nationprefix=False, nationprefix_sep=':'):
        if isinstance(schacpersonaluniqueids, str):
            schacpersonaluniqueids = [schacpersonaluniqueids]
        # R&S format
        rs_regexp = (r'(?P<urn_prefix>urn:schac:personalUniqueID:)?'
                     r'(?P<nation>[a-zA-Z]{2}):'
                     r'(?P<doc_type>[a-zA-Z]{2,3}):(?P<uniqueid>[\w]+)')
        for uniqueid in schacpersonaluniqueids:
            result = re.match(rs_regexp, uniqueid, re.I)
            if result:
                data = result.groupdict()
                # if data.get('nation') == 'IT' and data.get('doc_type') in  ['CF', 'TIN']:
                if nationprefix:
                    # returns IT:CODICEFISCALE
                    return nationprefix_sep.join((data['nation'], data['uniqueid']))
                # returns CODICEFISCALE
                return data['uniqueid']

    @staticmethod
    def matricola(personalUniqueCodes=[], id_string='dipendente', orgname='unical.it'):
        if isinstance(personalUniqueCodes, str):
            personalUniqueCodes = [personalUniqueCodes]
        _regexp = (r'(?P<urn_prefix>urn:schac:personalUniqueCode:)?'
                   r'(?P<nation>[a-zA-Z]{2}):'
                   # r'(?P<organization>[a-zA-Z\.\-]+):'
                   'ORGNAME:'
                   'IDSTRING:'
                   r'(?P<uniqueid>[\w]+)').replace('IDSTRING', id_string).replace('ORGNAME', orgname)
        for uniqueid in personalUniqueCodes:
            result = re.match(_regexp, uniqueid, re.I)
            if result:
                return result.groupdict()['uniqueid']


class UnicalAttributeGenerator:

    @staticmethod
    def matricola_dipendente(attributes):
        if attributes.get('schacPersonalUniqueCode'):
            return UnicalAttributeProcessor.matricola(attributes['schacPersonalUniqueCode'],
                                                      id_string='dipendente')

    @staticmethod
    def matricola_studente(attributes):
        if attributes.get('schacPersonalUniqueCode'):
            return UnicalAttributeProcessor.matricola(attributes['schacPersonalUniqueCode'],
                                                      id_string='studente')

    @staticmethod
    def codice_fiscale(attributes):
        if attributes.get('schacPersonalUniqueID'):
            return UnicalAttributeProcessor.codice_fiscale_rs(attributes['schacPersonalUniqueID'])


    # GARR - European Student Identifier
    @staticmethod
    def schacPersonalUniqueCodeESI(matricola_studente, orgname='unical.it'):
        return f"urn:schac:personalUniqueCode:int:esi:{orgname}:{matricola_studente}"


    @classmethod
    def process(cls, attributes, sp_mapping):
        codice_fiscale = cls.codice_fiscale(attributes)
        matricola_dipendente = cls.matricola_dipendente(attributes)
        matricola_studente = cls.matricola_studente(attributes)
        
        cattr = dict(
            matricola_dipendente=matricola_dipendente,
            matricola_studente=matricola_studente,
            codice_fiscale=codice_fiscale,
        )

        if matricola_studente:
            schacPersonalUniqueCodeESI = cls.schacPersonalUniqueCodeESI(matricola_studente=matricola_studente)
            cattr['schacPersonalUniqueCode'] = schacPersonalUniqueCodeESI
            
        for k, v in cattr.items():
            if v and k in sp_mapping:
                attributes[k] = v
        return attributes
