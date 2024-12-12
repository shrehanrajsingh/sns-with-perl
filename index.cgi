#!/usr/bin/perl

require './utils.cgi';
require './conn.cgi';

my $q = new CGI;

print $q->header("text/html");

util::open_html("index.html");
