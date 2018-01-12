##############################################################################
# Copyright (C) 2007-2018 Laboratório de Sistemas e Tecnologia Subaquática   #
# Departamento de Engenharia Electrotécnica e de Computadores                #
# Rua Dr. Roberto Frias, 4200-465 Porto, Portugal                            #
##############################################################################
# Author: Ricardo Martins                                                    #
##############################################################################

XML := IMC.xml
XSD := IMC.xsd

validate:
	@echo "* Validating $(XSD)..."
	@xmllint -noout -schema 'http://www.w3.org/2001/XMLSchema.xsd' $(XSD)
	@echo "* Validating $(XML)..."
	@xmllint -noout $(XML)
	@echo "* Validating $(XML) against $(XSD)..."
	@xmllint -noout -schema $(XSD) $(XML)

doc:
	@echo "* Generating documentation..."
	@python doc/generate.py

clean:
	@echo "* Cleaning sources..."
	@$(RM) -rf doc/__pycache__ doc/reference

.PHONY: validate doc clean
