export PROJECT_NAME = mmc-web-base
export VERSION = 2.3.1

export RPMBUILD = rpmbuild -ba
export BUILD = $(CURDIR)/build

export TARBALL = $(PROJECT_NAME)-$(VERSION)
export RELEASES_DIR = releases
export TARBALL_BZ = $(TARBALL).tar.bz2
export TARBALL_GZ = $(TARBALL).tar.gz
export EXCLUDE_FILES = --exclude .svn
export CPA = cp -af

export RPM_DIR = $(shell if [ -e ~/.rpmmacros ]; then cat ~/.rpmmacros | grep _topdir | sed "s/^.*\s//"; else echo ""; fi)
export RPM_SPEC = mmc-web-base.spec
export RPM_SPEC_DIR = $(shell if [ "`lsb_release -sri`" = "RedHatEnterpriseServer 5" ]; then echo "packages/rpm/redhat/el5/" ; elif [ "`lsb_release -sri`" = "RedHatEnterpriseAS 4" ]; then echo "packages/rpm/redhat/el4/" ; elif [ "`lsb_release -sri`" = "RedHatEnterpriseServer 5.1" ]; then echo "packages/rpm/redhat/el5/"; elif [ "`lsb_release -sri`" = "RedHatEnterpriseES 4" ]; then echo "packages/rpm/redhat/el4/"; else echo ""; fi)
export RPM_SPEC_FULLPATH = $(RPM_SPEC_DIR)/$(RPM_SPEC)

rpm: $(RELEASES_DIR)/$(TARBALL_GZ)
ifeq ($(RPM_DIR),)
	echo "RPM_DIR is void, you probably have no .rpmmacros"
else
	@echo "We may exit here if we didn't succeed to detect the distribution"
	exit $(shell if [ -z $(RPM_SPEC_DIR) ]; then echo 1; fi)
	rm -fr $(RPM_DIR)
	mkdir -p $(RPM_DIR)/{SOURCES,SPECS,BUILD,SRPMS,RPMS/i586}
	$(CPA) $(RELEASES_DIR)/$(TARBALL_GZ) $(RPM_DIR)/SOURCES
	cat $(RPM_SPEC_FULLPATH) | sed "s/__VERSION__/$(VERSION)/" > $(RPM_DIR)/SPECS/$(RPM_SPEC)
	$(CPA) $(RPM_SPEC_DIR)/*.diff $(RPM_DIR)/SOURCES
endif

# build the RPMs in a directory inside the source tree
buildrpms: RPM_DIR = $(BUILD)
buildrpms: rpm
	$(RPMBUILD) --define "_topdir $(RPM_DIR)" $(RPM_DIR)/SPECS/$(RPM_SPEC)
