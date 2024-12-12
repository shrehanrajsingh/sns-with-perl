#!/usr/bin/perl

require './utils.cgi';

sub parse_form_data {
    if ( $ENV{REQUEST_METHOD} eq 'GET' ) {
        my @vars = split /&/, $ENV{QUERY_STRING};
        my %qnames;

        for my $nv ( @vars ) {
            my ( $name, $value ) = split /=/, $nv;

            $qnames{$name} = $value;
        }

        if ( exists $qnames{'name'} ) {
            util::open_file("./assets/$qnames{'name'}");
        } else {
            # Send appropriate error code and message
        }
    }
};

parse_form_data ();