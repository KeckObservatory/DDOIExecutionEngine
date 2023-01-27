class OBDM():
    def __init__(self, ob):
        self.ob = ob
        self._parse_ob()
 
    def _parse_ob(self):
        """Init helper function
        """
        self.ob_id = self.ob.get('_ob_id', None)
        self.metadata = self.ob.get('metadata', None)
        self.acquisition = self.ob.get('acquisition', None)
        self.science = self.ob.get('science', None)
        self.target = self.ob.get('target', None)
        self.COMPONENTS = ['metadata', 'acquisition', 'science', 'target']

    def get_script(self, name, version):
        """Retrieves a string of a high level telescope command, 
        to be intrepreted by python thru a lookup table.
        """
        return self.ob.get('scripts', name, version)

    def get_component(self, keyword):
        """Sequence is a portion of the data. 
        """
        assert keyword in self.COMPONENTS, f'keyword: {keyword} not in {self.COMPONENTS}' 
        return self.__dict__.get(keyword, False)