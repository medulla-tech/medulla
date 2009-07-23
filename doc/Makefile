PULSE2_FOLDERS=conf dev install user

html:
	mkdir build
	cp -r $(PULSE2_FOLDERS) build
	-find build -name .svn -exec rm -fr {} \;
	for f in `find build -name \*xml`; do \
		echo $$f; \
		xmlto -o `dirname $$f` -m param.html.xsl xhtml-nochunks $$f; \
		rm -f $$f; \
		tidy -utf8 $${f%.xml}.html > $${f%.xml}.prehtml; \
		./mandrify $${f%.xml}.prehtml $${f%.xml}.html; \
		rm -f $${f%.xml}.prehtml; \
	done

tar: build
	(cd build; tar czf ../pulse2-doc.tar.gz $(PULSE2_FOLDERS))

clean:
	rm -fr build
