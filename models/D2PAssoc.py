__author__ = 'nicole'

from rdflib.namespace import OWL, RDF, DC
from rdflib import Namespace, URIRef, Literal
import re
import urllib
from models.Assoc import Assoc

#The first of many associations
#This one is specific for making a disease-to-phenotype
class D2PAssoc(Assoc):
        #FIXME init might not require all these elements
        has_phenotype="RO:0002200" #has_phenotype
        CLASS="owl:Class"
        IND="owl:NamedIndividual"

        #need to rewrite this way:
        #http://purl.obolibrary.org/obo/HP_0000750

        def __init__(self,assoc_id,entity_id,phenotype_id,onset,frequency,pub,evidence_code):
            self.annot_id=assoc_id
            self.entity_id = entity_id
            self.phenotype_id = phenotype_id
            self.onset = onset
            self.frequency = frequency
            self.pub_id = pub
            self.evidence = evidence_code
            self.rel = self.has_phenotype  #default to has_phenotype

            return

        def set_relationship(self,rel):
            self.rel = rel
            return

        def printTypes(self,filewriter=None):
            numStatements = 4
            print(self.entity_id,"rdf:type",self.CLASS,file=filewriter)
            print(self.phenotype_id,"rdf:type",self.CLASS,file=filewriter)
            print(self.pub_id,"rdf:type",self.IND,file=filewriter)
            print(self.evidence,"rdf:type",self.CLASS,file=filewriter)
            return numStatements

        def printAssociation(self,filewriter=None):
            numStatements = 6
            #note we are making the assumption that all classes will have their
            #labels printed elsewhere
            #this will return the number of statements printed
            print(self.entity_id,self.rel,self.phenotype_id,".", sep=" ",file=filewriter)
            #TODO is this "type" correct?
            #TODO do we need the relationship as a predicate here?
            print(self.annot_id, "rdf:type","Annotation:",".", sep=" ",file=filewriter)
            print(self.annot_id, ":hasSubject", self.entity_id, sep=" ",file=filewriter)
            print(self.annot_id, ":hasObject", self.phenotype_id, sep=" ",file=filewriter)
            print(self.annot_id, "dc:source", self.pub_id, sep=" ",file=filewriter)
            print(self.annot_id, "dc:evidence", self.evidence, sep=" ", file=filewriter)
            if (self.frequency is not None and self.frequency != ''):
                #FIXME what is the real predicate here?
                print(self.annot_id, ":frequencyOfPhenotype", self.frequency,file=filewriter)
                numStatements += 1
            if (self.onset is not None and self.onset != ''):
                print(self.annot_id, ":onset", self.onset,file=filewriter)
                numStatements += 1
            return numStatements

        def addAssociationNodeToGraph(self,g):
            namespaces = self.namespaces
            n = Namespace(namespaces['MONARCH'])
            node = n[self.annot_id]
#            s = n[self.entity_id.replace(':','_')]
            s = URIRef(self.entity_id)
            p = n[self.rel]
            #TODO generalize mapping curie to namespace
            o = Namespace(namespaces['HP'])[self.phenotype_id.replace('HP:','')]

            #scrub the occasional case errors in the pubs
            self.pub_id = self.pub_id.replace('pmid','PMID')
            if (re.compile('http').match(self.pub_id)):
                source = URIRef(self.pub_id)
#                source = URIRef(urllib.parse.urlencode(self.pub_id))
                #source = URIRef(urllib.parse.quote_plus(self.pub_id))
            elif (re.compile('PMID').match(self.pub_id)):
                source = Namespace(namespaces['PMID'])[self.pub_id.replace('PMID:','')]
            else:
                #default to a literal
                source = Literal(self.pub_id)
            evidence = Namespace(namespaces['ECO'])[self.evidence.replace('ECO:','')]
            frequency = onset = None

            g.add((s,RDF['type'],OWL['class']))
            g.add((o,RDF['type'],OWL['class']))
            g.add((s,p,o))

            g.add((node, RDF['type'],OWL['annotation']))
            g.add((node, OWL['hasSubject'], s))
            g.add((node, OWL['hasObject'], o))
            g.add((node, DC['source'], source))
            g.add((source,RDF['type'], OWL['NamedIndividual']))
            g.add((node, DC['evidence'], evidence))

            if (self.frequency is not None and self.frequency != ''):
                #FIXME what is the real predicate here?
                g.add((node, OWL['frequencyOfPhenotype'],Literal(self.frequency)))
            if (self.onset is not None and self.onset != ''):
                #FIXME what is the real predicate here?
                g.add((node,OWL['onset'],n[self.onset]))

#            print(g.serialize(format="turtle").decode())
            return g