""" This module defines the Python class passport used in ONIX"""

import math as m
from . import data as d
from .utils import functions as fct

class Passport(object):
    """Passport stores all the relevant data of indivudual nuclides and offers methods to extract information on them.

       The passport class is individually instantiated for each nuclide. It contains two types of information: constant and variable data.
       Constant data, such as the atomic mass, decay constant or the element's family (actinide or fission products) do not change over the course of a simulation.
       Variable data such as cross sections or fission yields do vary during a simulation and need to be updated regularly during a simulation.
       Some of the data are created at the time of the instantiation of the class such as the element's family or the nuclide's
       neutron reaction daughters. Other type of data, typically large in size such as cross sections and decay constants, are to be explicitly set or loaded by the code or by the user.

       Parameters
       ----------
       nuc_id : str
            Name or z-a-m id of the nuclide.
    
    """

    _mass = None
    _fission_E = None

    _name = None
    _zamid = None

    #_allreacs_dic_list = [] # A list of dicts of all the creation and destruction terms at eacch sequence point


    # Number id of the nuclide for which a passport is instantiated
    def __init__(self, nuc_id):

        self.nuc_id = nuc_id # probably useless
        if self._get_id_input_type(nuc_id) == 'name':
            self._name = self.nuc_id
            self._zamid = fct.name_to_zamid(self._name)
        elif self._get_id_input_type(nuc_id) == 'zamid':
            self._zamid = self.nuc_id
            self._name = fct.zamid_to_name(self._zamid)

        self._set_state()

        self._set_xschild()
        self._set_decaychild()
        self._set_xsparent()
        self._set_decayparent()
        self._set_all_parent()
        self._set_all_child()
        # self._all_non0_child = self.get_all_non0_child()

        self._all_reacs_dic = None
        self._allreacs_dic_list = []
        self.__current_sorted_allreacs_tuple_list = None
        self._sorted_allreacs_tuple_mat = []

        self._current_dens = None
        self._dens_seq = None
        self._current_dens_subseq = None
        self._dens_subseq_mat = None

        self._current_xs = None
        self._xs_seq = None
        self._decay_a = None
        self._decay_b = None
        self._fy = None

        if self.get_FAM() == 'ACT':
            self._set_energy_per_fission()





    @property
    def mass(self):
        """Returns the atomic mass of the nuclide in grams"""
        if self._mass is None:
            pass  # define exception for undefined variable
        return self._mass

    @mass.setter
    def mass(self, new_mass):
        """Sets the atomic mass of the nuclide in grams"""

        self._mass = new_mass    

    # Passport instantiation will read and extract by itself mass for the corresponding nuclide
    def load_mass(self):
        """Loads the atomic mass of the nuclide in gram.

        This method directly fetches the atomic mass from the mass library and automatically sets it
        to the passport object"""

        zamid = self._zamid
        zaid = zamid[:-1]

        # Some (rare) nuclides (for example Ag133 from ENDFVIII) are not in the mass library
        # For these nuclides, the mass number is used for the mass
        if zaid not in d.default_atm_mass_lib:
            mass = int(zaid[-3:])

        else:
            mass = d.default_atm_mass_lib[zaid]


        self._mass = mass



    @property
    def decay_a(self):
        """Returns the absolute values of the decay constant of the nuclide"""
        if self._decay_a is None:
            pass  # define exception for undefined variable
        return self._decay_a

    @property
    def decay_b(self):
        """Returns the fraction percent values of the decay constant of the nuclide"""
        if self._decay_b is None:
            pass  # define exception for undefined variable
        return self._decay_b

    @decay_a.setter
    def decay_a(self, new_decay_a):
        """Sets the absolute values of the decay constant of the nuclide"""

        self._decay_a =  new_decay_a

    @decay_b.setter
    def decay_b(self, new_decay_b):
        """Sets the fraction percent values of the decay constant of the nuclide"""
        self._decay_b =  new_decay_b

    def set_decay(self, decay_a, decay_b):
        """Sets the absolute and fracional values of the decay constant of the nuclide"""
        self.decay_a =  decay_a
        self.decay_b =  decay_b

    def load_decay(self):
        """Loads the decay constant value of the nuclide.

        This method directly fetches the decay constant values (absolute and fractional) from the decay library and automatically sets it to the passport object"""

        zamid = self._zamid

        decay_a = d.default_decay_lib_a[zamid]
        decay_b = d.default_decay_lib_b[zamid]

        self.decay_a = decay_a
        self.decay_b = decay_b

    @property
    def current_xs(self):
        """Returns the current cross sections dictionnary of the nuclide"""
        if self._current_xs is None:
            pass  # define exception for undefined variable
        return self._current_xs

    @current_xs.setter
    def current_xs(self, new_xs):
        """Sets the current cross sections dictionnary of the nuclide"""
        self._current_xs = new_xs

    @property
    def xs_seq(self):
        """Returns the sequence of cross section dictionnaries of the nuclide"""
        return self._xs_seq

    @xs_seq.setter
    def xs_seq(self, new_xs_seq):
        """Sets the sequence of cross section dictionnaries of the nuclide"""
        self._xs_seq = new_xs_seq

    def _append_xs_seq(self, new_xs):
        """Appends a new cross section dictionnary to the sequence of cross section dictionnaries"""
        self._xs_seq.append(new_xs)

    def _set_xs(self, new_xs):
        """This method first verifies if a macro sequence of cross section dictionnaries has been already created for the nuclide.
        If not, it creates a sequence and append the new cross section dictionnary.
        If a sequence already exists, it just appends the new dictionnary to the already existing sequence"""
        # If this is the fist step
        if self.current_xs == None:
            self.xs_seq = [new_xs]
        else:
            self._append_xs_seq(new_xs)

        self.current_xs = new_xs
       # self._append_time_subseq_mat()

    def _overwrite_xs(self, new_xs):
        """This method first verifies if a macro sequence of cross section dictionnaries has been already created for the nuclide.
        If not, it creates a sequence and append the new cross section dictionnary.
        If a sequence already exists, it overwrites the last dictionnary with the new dictionnary in the already existing sequence"""
       # If this is the fist step
        if self.current_xs == None:
            self.xs_seq = [new_xs]
        else:
            self.xs_seq[-1] = new_xs

        self.current_xs = new_xs
       # self._append_time_subseq_mat()


    # Passport instantiation will read and extract by itself mass for the corresponding nuclide
    def load_xs(self):
        """Loads the cross sections data of the nuclide.

        This method directly fetches the cross sections data from the cross section library and automatically sets
        it to the passport object"""

        zamid = self._zamid
        xs_lib = d.default_xs_lib
        xs = xs_lib[zamid]

        self._current_xs = xs



    @property
    def fy(self):
        """Returns the fission yields dictionnary.

        Fission yield dictionnary are defined per fission product. Each key of the dictionnary is the zamid of one of the 
        fission parents and the corresponding entry is the fission yield normalized to 1 (value between 0 and 1)"""

        if self._fy is None:
            pass  # define exception for undefined variable)
        return self._fy

    @fy.setter
    def fy(self, new_fy):
        """Sets the fission yields dictionnary to a nuclide

        Parameters
        ----------
        new_fy : dict
            Dictionnary of fission yields for a daughter nuclide

        """

        if self.get_FAM == 'ACT':
            raise Not_a_Fission_Product("{} is not a FP and can't be given fission yields".format(self._zamid))
        self._fy = new_fy

    # Passport instantiation will read and extract by itself mass for the corresponding nuclide
    def load_fy(self):
        """Load the fission yields dictionnary of the nuclide

        This method directly fetches the fission yields data from the fission yield library and automatically sets
        it to the passport object

        If the nuclide for which the fission yields data are being loaded is not a fission product,
        the error onix.Not_a_Fission_Product will be raised"""

        if self.get_FAM() == 'ACT':
            raise Not_a_Fission_Product("{} is not a FP and can't be given fission yields".format(self._zamid))

        zamid = self._zamid
        fy_lib = d.default_fy_lib
        fy = fy_lib[zamid]

        self._fy = fy



    @property
    def current_dens(self):
        """Returns the current density of the nuclide in atom per :math:`cm^{3}`"""
        if self._current_dens is None:
            pass  # define exception for undefined variable
        return self._current_dens

    @current_dens.setter
    def current_dens(self, new_dens):
        """Sets the current density of the nuclide in atom per :math:`cm^{3}`"""
        self._current_dens = new_dens

    @property
    def dens_seq(self):
        """Returns the macro sequence of densities of the nuclide in atom per :math:`cm^{3}`"""
        return self._dens_seq

    @dens_seq.setter
    def dens_seq(self, new_dens_seq):
        """Sets the macro sequence of densities of the nuclide in atom per :math:`cm^{3}`"""

        self._dens_seq = new_dens_seq

    def _append_dens_seq(self, new_dens):
        """Appends a new density value to the macro sequence of densities of the nuclide in atom per :math:`cm^{3}`"""
        self._dens_seq.append(new_dens)

    def get_current_dens_subseq(self):
        """Returns the current micro sequence of densities (i.e. micro sequence corresponding to the current macro step)"""
        return self._dens_subseq_mat[-1]

    @property
    def dens_subseq_mat(self):
        """Returns the list of micro sequences of densities (one per macro step)"""
        return self._dens_subseq_mat

    def get_dens_subseq(self, s):
        """Returns the micro sequence of densities number s (i.e. micro sequence corresponding to the macro step number s)"""
        return self._dens_subseq_mat[s]

    def _append_dens_subseq_mat(self, new_dens, ss):
        """Sets new density value to the list of micro sequences of densities

        If this is the first micro step, creates a new micro sequence"""
        if ss == 0:
            self._dens_subseq_mat.append([])
        self._dens_subseq_mat[-1].append(new_dens)

    def _set_initial_dens(self, new_dens):
        """Sets initial density"""
        self.current_dens = new_dens
        self.dens_seq = [new_dens]
        self._dens_subseq_mat = [[new_dens]]

    def _set_step_dens(self):
        """Sets a new density in the macro sequence of densities

        The current density is set to the new density
        The new density is appended to the macro sequence of densities"""
        dens = self.current_dens
        self._append_dens_seq(dens)

    def _set_substep_dens(self, dens, ss):
        """Sets a new density in the micro sequence of densities

        The current density is set to the new density
        The new density is appended to the micro sequence of densities"""
        self.current_dens = dens
        self._append_dens_subseq_mat(dens, ss)
       




    @property
    def zamid(self):
        """Returns the z-a-m-id of the nuclide"""
        return self._zamid

    @property
    def name(self):
        """Returns the name of the nuclide"""
        return self._name


    def _get_xs_prod_from_dic(self):
        """Produces a dictionnary that contains the operations required to be done on the zamid number of the nuclide
        to obtain the zamid of nuclides produced by the different types of neutron-induced reaction"""
        state = self._state
        if state == 0:
            xs_prod_from = d.xs_prod_fromS_toS.copy()
            xs_prod_from.update(d.xs_prod_fromS_toX)

        elif state == 1:
            xs_prod_from = d.xs_prod_fromX_toS.copy()
            xs_prod_from.update(d.xs_prod_fromX_toX)

        return xs_prod_from

    def _get_decay_prod_from_dic(self):
        """Produces a dictionnary that contains the operations required to be done on the zamid number of the nuclide
        to obtain the zamid of nuclides produced by the different types of decay reaction"""
        state = self._state
        if state == 0:
            decay_prod_from = d.decay_prod_fromS_toS.copy()
            decay_prod_from.update(d.decay_prod_fromS_toX)

        elif state == 1:
            decay_prod_from = d.decay_prod_fromX_toS.copy()
            decay_prod_from.update(d.decay_prod_fromX_toX)

        return decay_prod_from

    def _get_xs_prod_to_dic(self):
        """Produces a dictionnary that contains the operations required to be done on the zamid number of other nuclides
        that produces the nuclide via different types of neutron-induced reaction"""
        state = self._state
        if state == 0:
            xs_prod_to = d.xs_prod_fromS_toS.copy()
            xs_prod_to.update(d.xs_prod_fromX_toS)

        elif state == 1:
            xs_prod_to = d.xs_prod_fromS_toX.copy()
            xs_prod_to.update(d.xs_prod_fromX_toX)

        return xs_prod_to

    def _get_decay_prod_to_dic(self):
        """Produces a dictionnary that contains the operations required to be done on the zamid number of other nuclides
        that produces the nuclide via different types of decay reaction"""
        state = self._state
        if state == 0:
            decay_prod_to = d.decay_prod_fromS_toS.copy()
            decay_prod_to.update(d.decay_prod_fromX_toS)

        elif state == 1:
            decay_prod_to = d.decay_prod_fromS_toX.copy()
            decay_prod_to.update(d.decay_prod_fromX_toX)

        return decay_prod_to



    @property
    def xs_child(self):
        """Returns the daughter products of the nuclide via neutron-induced rections"""
        return self._xs_child    

    def _set_xschild(self):

        zamid = int(self._zamid)

        xs_prod_from_dic = self._get_xs_prod_from_dic()
        
        child_dic = {}
      
        for i in xs_prod_from_dic:

            # If nuclide is Li6 or Be10, add children from (n,t)
            # (n,t) rxn rate only tallied for Li6 and Be10
            if i == '(n,t)':
                if zamid in [30060, 50100]:
                    # In the case of (n,t) (and (n,alpha) as well), the reaction creates two new nuclides
                    # The reaction is thus branched out in two new reactions:
                    # 1) (n,x) which creates nuclides according to xs_prod_from_dic
                    # 2) (n,x)x which creates x, which is the particle emitted (tritium or alpha)
                    child_dic['(n,t)t'] = '10030'
            
                elif zamid not in [30060, 50100]:
                    continue

                # Note that after that, Li6 and Be10 are still being added the other child from (n,t), as below

            child_zamid = zamid + 10000*xs_prod_from_dic[i][0]+ 10*xs_prod_from_dic[i][1] + xs_prod_from_dic[i][2]
            child_dic[i] = str(child_zamid)

        self._xs_child = child_dic

    @property
    def decay_child(self):
        """Returns the daughter products of the nuclide via decay reactions"""
        return self._decay_child

    def _set_decaychild(self):

        zamid = int(self._zamid)

        decay_prod_from_dic = self._get_decay_prod_from_dic()
        
        child_dic = {}
        
        for i in decay_prod_from_dic:
            child_zamid = zamid + 10000*decay_prod_from_dic[i][0]+ 10*decay_prod_from_dic[i][1] + decay_prod_from_dic[i][2]
            child_dic[i] = str(child_zamid)

        self._decay_child = child_dic

    @property
    def xs_parent(self):
        """Returns the parents of the nuclide via neutron-induced reactions"""
        return self._xs_parent

    def _set_xsparent(self):

        zamid = int(self._zamid)

        parent_dic = {}

        xs_prod_to_dic = self._get_xs_prod_to_dic()
        
        for i in xs_prod_to_dic:

            if i == '(n,t)':

                # If nuclide is not a possible children of (n,t) reaction of Li6 or Be10
                # Skip
                if zamid not in [10030,20040, 30070]:
                    continue

                # In the case of tritium itself, the nuclide has two parents from the same type
                # of reaction (Li6 and Be10 from (n,t))
                # Therefore, we branched out this channel into two new channels
                # Note that ONIX should not try to find a parent for tritium through xs_prod_to_dic in this case
                # It would track back to Helium5 (He5 +n = H3 + H3)), which itself has no (n,t) reaction allocated
                if zamid == 10030:
                    parent_dic['Li6(n,t)'] = '30060'
                    parent_dic['Be10(n,t)'] = '50100'
                    continue

                # This leaves us with only He4 and Li7 who are the products of Li6 (n,t) and Be10 (n,t) respectively
                # For these two nuclides, ONIX finds the parents through xs_prod_to_dict as below

            parent_zamid = zamid - 10000*xs_prod_to_dic[i][0]- 10*xs_prod_to_dic[i][1] - xs_prod_to_dic[i][2]
            parent_dic[i] = str(parent_zamid)

        self._xs_parent = parent_dic

    @property
    def decay_parent(self):
        """Returns the parents of the nuclide via decay reactions"""
        return self._decay_parent

    def _set_decayparent(self):

        zamid = int(self._zamid)
        
        parent_dic = {}

        decay_prod_to_dic = self._get_decay_prod_to_dic()
        
        for i in decay_prod_to_dic:
            parent_zamid = zamid - 10000*decay_prod_to_dic[i][0]- 10*decay_prod_to_dic[i][1] - decay_prod_to_dic[i][2]
            parent_dic[i] = str(parent_zamid)

        self._decay_parent = parent_dic

    @property
    def all_parent(self):
        """Returns all parents of the nuclide"""
        return self._all_parent

    def _set_all_parent(self):

        xs_parent = self._xs_parent
        decay_parent = self._decay_parent
        parent_list = []

        for i in xs_parent:
            parent_list.append(xs_parent[i])
        for i in decay_parent:
            parent_list.append(decay_parent[i])

        self._all_parent = parent_list

    @property
    def all_child(self):
        """Returns all daughter products of the nuclide."""
        return self._all_child

    def _set_all_child(self):

        xs_child = self._xs_child
        decay_child = self._decay_child
        child_list = []

        for i in xs_child:
            child_list.append(xs_child[i])
        for i in decay_child:
            child_list.append(decay_child[i])

        self._all_child = child_list

    @property
    def fission_child(self):
        """Returns daughter products of the nuclide via fission reactions."""
        return self._fission_child

    @fission_child.setter
    def _fission_child(self, fission_child):


        # I am not sure why I set this error
        # If the parent has no cross section, it is ok to still list its fission child
        # if self._current_xs == None:
        #     raise XS_not_yet_set("{} has no cross-sections yet".format(self._zamid))

        # Same here. Might not be important
        # if 'fission' not in self._current_xs:
        #     raise No_fission_XS("{} has no fission cross-sections".format(self._zamid))

        self._fission_child = fission_child


    # Non0 parent and child are only the relatives when the reaction that link them to the nuclide is non-zero

    # def get_all_non0_parent(self):

    #     xs_parent = self._xs_parent
    #     decay_parent = self._decay_parent
    #     parent_list = []

    #     for i in xs_parent:
    #         parent_list.append(xs_parent[i])
    #     for i in decay_parent:
    #         parent_list.append(decay_parent[i])

    #     return parent_list

    # @property
    # def all__non0_parent(self):

    #     return self._all_parent

    # On the fly calculation
    def get_all_non0_child(self):
        """Gets all daughter products of the nuclide produced via reactions that are non-zero (i.e., the reaction cross section or decay constant is not null) in the library used in the simulation"""
        xs_child = self._xs_child
        decay_child = self._decay_child
        non0_child_list = []
        xs = self._current_xs
        decay_a = self._decay_a
        state = self._state

        if xs != None:

            for i in xs_child:
                # If this is an excited state, you need to remove the X at the beginning of the reaction name
                if state ==1:
                    j = i[1:]
                elif state == 0:
                    j = i
                if j in xs:
                    if xs[j][0] != 0:
                        non0_child_list.append(xs_child[i])

        if decay_a != None:

            for i in decay_child:
                # If this is an excited state, you need to remove the X at the beginning of the reaction _name
                if state ==1:
                    j = i[1:]
                elif state == 0:
                    j = i
                if j in decay_a:
                    if decay_a[j] != 0:
                        non0_child_list.append(decay_child[i])

        return non0_child_list

    # On the fly calculation since an AVT can become a FP if fy is set
    def get_FAM(self):
        """Returns the family of a nuclide (AVT= Activation, FP= Fission Product, ACT= Actinide)"""

        nz = self.get_z

        FAM = 'AVT'
        if self._fy != None:
            FAM = 'FP'
        elif nz > 89:
            FAM= 'ACT'

        return FAM

    @property
    def get_a(self):
        """Returns the mass number of the nuclide"""
        zaid = self._zamid

        if len(zaid) == 5:
            a = int(zaid[1:4])
        else:
            a = int(zaid[2:5])

        return a

    @property
    def get_z(self):
        """Returns the atomic number of the nuclide"""
        zaid = self._zamid

        if len(zaid) == 5:
            z = int(zaid[0:1])
        else:
            z = int(zaid[0:2])

        return z

    @property
    def state(self):
        """Return the excitation state of the nuclide (excited or ground state)"""

        return self._state

    def _set_state(self):
        """Sets the excitation state of the nuclide (excited or ground state)"""
        zamid = self._zamid
        state = int(zamid[-1])

        self._state = state

    def _get_id_input_type(self, nuc_id):

        if fct.is_int(nuc_id) == True:
            id_type = 'zamid'
        else:
            id_type = 'name'

        return id_type

    @property
    def fission_E(self):
        """Returns the fission energy of the nuclide"""
        return self._fission_E

    @fission_E.setter
    def fission_E(self, fission_E):
        """Sets the fission energy of the nuclide"""
        self._fission_E = fission_E

    def _set_energy_per_fission(self):

        a = self.get_a
        z = self.get_z
        fission_E = 1.29927e-3*(z**2)*(a**0.5) + 33.12

        self._fission_E = fission_E

    def get_natural_abundance(self):
        """Gets the natural abundance of the nuclide normalized to 1 (value between 0 and 1)"""
        name_new_format = fct.onix_name_to_openmc_name(self.name)
        nat_abun_dict = d.NATURAL_ABUNDANCE
        if name_new_format in nat_abun_dict:
            nat_abun = nat_abun_dict[name_new_format]
        else:
            nat_abun = 0.0

        return nat_abun


    @property
    def destruction_dic(self):
        """Returns a dictionnary of all the destruction terms of the nuclide.

        The keys are the reactions' names
        The entries are the reaction rates of the reactions in :math:`barn^{-1}cm^{-1}s^{-1}`"""
        return self._destruction_dic

    @destruction_dic.setter
    def destruction_dic(self, destruction_dic):
        """Sets a dictionnary of all the destruction terms of the nuclide"""
        self._destruction_dic = destruction_dic

    @property
    def creation_dic(self):
        """Returns a dictionnary of all the production terms of the nuclide.

        The keys are the parent nuclides' names with the reaction in parenthesis
        The entries are the reaction rates of the reactions in :math:`barn^{-1}cm^{-1}s^{-1}`"""
        return self._creation_dic

    @creation_dic.setter
    def creation_dic(self, creation_dic):

        self._creation_dic = creation_dic

    @property
    def allreacs_dic(self):
        """Returns an aggregated dictionnary with production and destruction terms of the nuclide"""
        return self._allreacs_dic

    @allreacs_dic.setter
    def allreacs_dic(self, allreacs_dic):

        self._allreacs_dic = allreacs_dic

    @property
    def allreacs_dic_list(self):
        """Returns a list of aggregated dictionnaries with production and destruction terms of the nuclide. One dictionnary per microstep"""

        return self._allreacs_dic_list

    def _allreacs_dic_list_append(self, allreacs_dic):

        self._allreacs_dic_list.append(allreacs_dic)

    @property
    def current_sorted_allreacs_tuple_list(self):

        return self._current_sorted_allreacs_tuple_list

    def _append_current_sorted_allreacs_tuple_list(self, sorted_allreacs, ss):

        # If this is the beginning of a new step
        if ss == 0:
            self._current_sorted_allreacs_tuple_list = []

        self._current_sorted_allreacs_tuple_list.append(sorted_allreacs)

    @property
    def sorted_allreacs_tuple_mat(self):
        """Returns a list of tuples that contains destruction and production terms

        For destruction terms, the first element is the reaction name and the second element
        is the reaction rate in :math:`barn^{-1}cm^{-1}s^{-1}`
        For production terms, the first element is the parent nuclide witht the reaction name in parenthesis
        and the second element is the reactio rate in :math:`barn^{-1}cm^{-1}s^{-1}`
        These tuples are ranked from lower reaction rate to higher reaction rate"""
        return self._sorted_allreacs_tuple_mat

    def _append_sorted_allreacs_tuple_mat(self):

        self._sorted_allreacs_tuple_mat.append(self.current_sorted_allreacs_tuple_list)

    @property
    def pikachu(self):

        return 'PIKA PIKA!'


class Incorrect_nuc_id(Exception):
    """Raise when the id input format in passport instantiation is incorrect"""
    pass

class Nuc_xs_not_found(Exception):
    """Raise when the user requests a cross-sections of a nuclide that is not in the nuclide set """
    pass

class Not_a_Fission_Product(Exception):
    """Raise when the user tries to set fission yields for a non fission product nuclide """
    pass

class XS_not_yet_set(Exception):
    """Raise when the user tries to access XS for a nuclide which XS have not been set yet """
    pass

class No_fission_XS(Exception):
    """Raise when the user tries to access fission XS for a nuclide which fission XS have not been set yet """
    pass





















































