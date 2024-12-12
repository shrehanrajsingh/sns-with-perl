#!/usr/bin/perl

package util;

use CGI;

my $q = new CGI;

sub open_html {
    my $fl = shift;
    open (HTML_FILE, "<", $fl) || die "Cannot open $fl\n";

    while (my $line = <HTML_FILE>) {
        print $line;
    }

    close (HTML_FILE);
};

sub open_file {
    my $name = shift;
    my @filesp = split /\./, $name;

    print $q->header ("text/$filesp[$#filesp]");

    open (FILE_HANDLE, "<", $name);

    while (my $line = <FILE_HANDLE>) {
        print $line;
    }

    close (FILE_HANDLE);
}

sub append_to_file {
    my $fname = shift;
    my $cont = shift;

    open (DB_F, ">>", $fname);
    print DB_F $cont . "\n";
    close (DB_F);
};

sub trim {
    my $data = shift;
    $data =~ s/^\s+|\s+$//g;
    return $data;
}

1;