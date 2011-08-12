<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!--
      Driver file for the transformation of docbook to xhtml.
      Mostly inspired by RefDB driver
       -->
  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/xhtml/docbook.xsl"/>
  
  <!-- some overrides of parameters defined in param.xsl -->
  <xsl:param name="section.autolabel" select="1"/>
  <xsl:param name="chunk.section.depth" select="0"/>
  <xsl:param name="use.svg" select="0"/>
  <xsl:param name="section.label.includes.component.label" select="1"/>
  
  <xsl:param name="admon.graphics" select="1"></xsl:param>
  <xsl:param name="admon.textlabel" select="0"></xsl:param>
  <xsl:param name="admon.graphics.path">/content/images/docbook/</xsl:param>

  <xsl:param name="funcsynopsis.style" select="'ansi'"/>

  <!-- xsl:template match="/" >
    <xsl:apply-imports />
  </xsl:template -->

  <xsl:template match="*" mode="process.root">
    <xsl:variable name="doc" select="self::*"/>

    <xsl:call-template name="user.preroot"/>
    <xsl:call-template name="root.messages"/>

    <html>
      <head>
	<xsl:call-template name="system.head.content">
	  <xsl:with-param name="node" select="$doc"/>
	</xsl:call-template>
	<xsl:call-template name="head.content">
	  <xsl:with-param name="node" select="$doc"/>
	</xsl:call-template>
	
	<style type="text/css">
	  @import url("http://pulse2.mandriva.org/custom/css/linbox.css");

	  .screen {
	    background-color: #FFEEDD;
	    padding: 2em;
	    -moz-border-radius: 8px;
	    -khtml-border-radius: 8px;
	    border-radius: 8px;
	  }

	  .note {
	    background-color: #DDEEFF;
	    margin: 2em;
	    margin-left: auto;
	    margin-right: auto;
	    width: 80% !important;
	    min-height: 40px;
	    clear: both;
	    text-align: justify;
	    vertical-align: middle;
	    border-collapse: collapse;
	    padding: 0.5em 1em 0.5em 36px;
	    background-position: 5px 0.5em;
	    background-repeat: no-repeat;
	    -moz-border-radius: 8px;
	    -khtml-border-radius: 8px;
	    border-radius: 8px;
	  }	
	</style>
      
      </head>
      <body>
	<xsl:call-template name="body.attributes"/>
	<div id="logolinbox" >
	  <img src="http://pulse2.mandriva.org/custom/mandriva.png" alt="mandriva" />
	</div>
	
	<div id="metanav" class="nav">
	  &#xA0;
	</div>
	
	<div id="internav">
	</div>
	
	<div id="mainnav" class="nav" style="overflow: none;">
	  &#xA0;
	</div>
	
	<div id="main">
	  <div id="singlecontent">
	    
	    <xsl:apply-templates select="."/>
	    
	  </div>
	</div>
	
	<!-- linbox footer section -->
	<div id="linbox_footer" class="small">
	  <div class="right" style="margin:0px 4px 0px 4px;">
	    &#xA9;&#xA0;&#xA0;2007-2011&#xA0;&#xA0;Mandriva&#xA0;Group
	  </div>
	  <br/>
	</div>
      </body>
    </html>
    <xsl:value-of select="$html.append"/>
  </xsl:template>

</xsl:stylesheet>
