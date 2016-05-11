#!/usr/bin/perl

use strict;
use warnings;
use DBI;
use CGI qw/:standard/;
#use CGI::Carp qw/ fatalsToBrowser warningsToBrowser/;
require '/home/bif724_161a18/.secret';
require '/home/bif724_161a18/public_html/Assignment1/tash_a1_lib.pl';
print "Content-type: text/html\n\n";

# password for making connection to mysql, stored as variable after calling subroutine
my $password = get_paswd();
my $sql = "select * from a1_data;";
my $sort = param('sort');

# connects to database, displays error if connection cannot be made
my $dbh =DBI->connect("DBI:mysql:host=db-mysql;database=bif724_161a18", "bif724_161a18", $password) or die "Problem connecting" . DBI->errstr;

# sql query statments for sorting by table header links
if (param()) { 
      if ($sort eq 'new') {
            $sql = "select * from a1_data;";
      }
      elsif ($sort eq 're1_id') {
            $sql = "select * from a1_data order by 're1_id';";
      }
      elsif ($sort eq 'score') {
            $sql = "select * from a1_data order by 'score' desc;";
      }
      elsif ($sort eq 'target') {
            $sql = "select * from a1_data order by 'gene_id' desc;";
      }
      else {
            print " ";
      }
}
else {
      $sql = "select * from a1_data;";
}
# prepares query, displays error is prepare cannot be made
my $sth = $dbh->prepare($sql) or die "Problem with prepare" . DBI->errstr;
# executes query, displays error is execute cannot be made
my $new_data = $sth->execute() or die "Problem with execute" . DBI->errstr;
# call subroutine which prints beginning of html, arguments are tab heading and css file
print begin_html("View All Records","tash_a1_view.css");
print <<T_HEADER;
      <p>This table displays the current data within the table. By clicking on the header links you can order the entries by re1ID, score or target gene id</p>

    <table class ="view">
   
            <tr><th><a href="http://zenit.senecac.on.ca/~bif724_161a18/Assignment1/tash_a1_view.cgi?sort=re1_id">Repressor Element 1 ID</a></th><th><a href="http://zenit.senecac.on.ca/~bif724_161a18/Assignment1/tash_a1_view.cgi?sort=score">Score</a></th>
            <th><a href="http://zenit.senecac.on.ca/~bif724_161a18/Assignment1/tash_a1_view.cgi?sort=target">Target Gene ID</a></th><th>Position of RE1</th><th>Sense</th><th>Description</th></tr>
T_HEADER
# if there is data within $new_data its value will be greater than 0
if ($new_data != 0) {
      # loops through if there is data
      while (my @row = $sth->fetchrow_array) {
        print "<div class ='test'><tr><td>$row[0]</td><td>$row[1]</td><td><a href='http://uswest.ensembl.org/Gene/Summary?db=core;g=$row[2]' target='_blank'>$row[2]</td><td>$row[3]</td><td>$row[4]</td><td>$row[5]</td></tr></div>";
      }
} else {
      # if new_data is = 0 it will print an error message
    print "<tr colspan='3'><td>no records found</td></tr>";
}
# drops database connection or prints error message
$dbh->disconnect() or die "Problem with disconnect" . DBI->errstr;
print "</table>";
# calls subroutine to print end of html
print end_html();
