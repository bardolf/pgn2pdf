#!/usr/bin/perl
#
# file_upload.pl - Demonstration script for file uploads
# over HTML form.
#
# This script should function as is.  Copy the file into
# a CGI directory, set the execute permissions, and point
# your browser to it. Then modify if to do something
# useful.
#
# Author: Kyle Dent
# Date: 3/15/01


use CGI;
use strict;

my $PROGNAME = "pgn2pdf.cgi";

my $cgi = new CGI();

#
# If we're invoked directly, display the form and get out.
#
if (! $cgi->param("button") ) {
	DisplayForm();
	exit;
}


#my $upfile = 'taktikadeti.pgn';

#
# We're invoked from the form. Get the filename/handle.
#
my $upfile = $cgi->param('upfile');

#
# Get the basename in case we want to use it.
#
my $basename = GetBasename($upfile);

#
# At this point, do whatever we want with the file.
#
# We are going to use the scalar $upfile as a filehandle,
# but perl will complain so we turn off ref checking.
# The newer CGI::upload() function obviates the need for
# this. In new versions do $fh = $cgi->upload('upfile'); 
# to get a legitimate, clean filehandle.
#
no strict 'refs';
#my $fh = $cgi->upload('upfile'); 
#if (! $fh ) {
#	print "Can't get file handle to uploaded file.";
#	exit(-1);
#}

#######################################################
# Choose one of the techniques below to read the file.
# What you do with the contents is, of course, applica-
# tion specific. In these examples, we just write it to
# a temporary file. 
#
# With text files coming from a Windows client, probably
# you will want to strip out the extra linefeeds.
########################################################

#
# Get a handle to some file to store the contents
#
if (! open(OUTFILE, ">/tmp/$upfile") ) {
	print "Can't open /tmp/$upfile for writing - $!";
	exit(-1);
}


#
# 1. If we know it's a text file, strip carriage returns
#    and write it out.
#
#while (<$upfile>) {
# or 
#while (<$fh>) {
#	s/\r//;
#	print OUTFILE "$_";
#}

#
# 2. If it's binary or we're not sure...
#
my $nBytes = 0;
my $totBytes = 0;
my $buffer = "";
# If you're on Windows, you'll need this. Otherwise, it
# has no effect.
binmode($upfile);
#binmode($fh);
while ( $nBytes = read($upfile, $buffer, 1024) ) {
#while ( $nBytes = read($fh, $buffer, 1024) ) {
	print OUTFILE $buffer;
	$totBytes += $nBytes;
}

close(OUTFILE);

#
# Turn ref checking back on.
#
use strict 'refs';

# more lame feedback
#print "thanks for uploading $basename ($totBytes bytes)<br>\n";	


#######################
# processing the file
#######################

# Preparing the FENs
my $file = "/tmp/$upfile";
my $counter = 0;
my $result = "";
open (my $INPUT, $file) or die "Could not open $file: $!";

while( my $line = <$INPUT>)  {      
    if ($line =~ /\[FEN ".*"\]/) {
        my $fen = $line =~ s/^\[FEN "(.*)"\]\s*$/$1/gr;         
        if ($counter % 2 == 1) {
            $result = $result."{$fen}";            
        } else {
            $result = $result."\n\\chezz{$fen}";
        }        
    	$counter++;    
    }    
}
close($INPUT);
if ($counter % 2 == 1) {
   $result = $result."{}";
}

# Reading the template
my $template = 'pgn2pdf.template';
my $final = "";
open ($INPUT, $template) or die "Could not open $template: $!";

while( my $line = <$INPUT>)  { 
    if ($line =~ /%%%CONTENT%%%/) {
        $final = $final.$result;
    } else {
        $final = $final.$line;
    }
}
close($INPUT);

# Writing to file
my $output = $file.".tex";
open(my $OUTPUT, '>', $output) or die "Could not open file '$output' $!";
print $OUTPUT $final;
close($OUTPUT);

# Calling latex
`cd /tmp && /usr/bin/pdflatex "$output";`;


# Servin file for download
print "Content-Type: application/x-download\n";
print "Content-Disposition: attachment; filename=$upfile.pdf\n\n";

open FILE,"< /tmp/$upfile.pdf" or die "Can't open: $!";
binmode FILE;
local $/ = \10240;
while (<FILE>) {
  print $_;
}
close FILE;




##############################################
# Subroutines
##############################################

#
# GetBasename - delivers filename portion of a fullpath.
#
sub GetBasename {
	my $fullname = shift;

	my(@parts);
	# check which way our slashes go.
	if ( $fullname =~ /(\\)/ ) {
		@parts = split(/\\/, $fullname);
	} else {
		@parts = split(/\//, $fullname);
	}

	return(pop(@parts));
}

#
# DisplayForm - spits out HTML to display our upload form.
#
sub DisplayForm {
print "Content-type: text/html\n\n";
print <<"HTML";
<html>
<head>
<title>pgn2pdf</title>
<body>
<h3>pgn2pdf</h3>
<form method="post" action="$PROGNAME" enctype="multipart/form-data">
Enter a file to upload: <input type="file" name="upfile"><br>
<input type="submit" name="button" value="Upload File">
</form>

HTML
}
