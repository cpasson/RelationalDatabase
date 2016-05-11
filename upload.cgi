#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/:standard/;
#use CGI::Carp qw/ fatalsToBrowser warningsToBrowser/;
use DBI;
#warningsToBrowser(1);
require '/home/bif724_161a18/public_html/Assignment1/tash_a1_lib.pl'; # subroutines containing html code
require '/home/bif724_161a18/.secret';

my $password = get_paswd();
my @error_lines;
my $success;
# check to see if file has been selected
if(param()) {
    my $upfile = param("upload_file");
    # checks for valid file name, if incorrect - displays error and ends program
    if ($upfile !~ /[\w-]+\.csv/) {
        print "Content-type: text/html\n\n\n";
        print begin_html("Upload a File", "tash_a1_add.css");
        print "Error with file name, can only contain letters, dashes and underscores. Must end in .csv";
        print &form();
        print end_html;
        exit;
    }
    my $upfh = upload("upload_file");
    # puts contents of file into array
    my @all_lines = <$upfh>;
    my $rows;
    # validates each data entry from file (each separated by line and split each field by ',')
    foreach (@all_lines) {
        my @ind_line = split(',', $_);      
        my $error_count = 0;
        my $check_dups = 1;
        my @dups;
        # validation for re1_id
        if ($ind_line[0] !~ /(opossum|human|rat|xenopus|chicken)_42_(\d{1,2}[a-z]?)_((W|X|Y|Z)|([1-9]|[1-7][0-9])|scaffold_\d{1,7})_(\d{1,9})_(r|f)/) {
            $error_count++;  # [1-9]|[1-7][0-9]
            $check_dups = 0;
        }
        # checking for whether data exists in db already
        if (my $check_dups == 1) { # means re1_id entered is valid
            my $dbh =DBI->connect("DBI:mysql:host=db-mysql;database=bif724_161a18", "bif724_161a18", $password) or die "Problem connecting" . DBI->errstr;
            my $count = "select count(*) from a1_data where re1_id = ?"; # statement to see if it exists already
            my $sth = $dbh->prepare($count) or die "problem with prepare in primary duplicate check" . DBI->errstr;
            my $dup_count = $sth->execute($ind_line[0]); # if it exists value will be 1 (defintely not 0)
            @dups = $sth->fetchrow_array;
        }
        if (@dups) {
            $error_count++; 
        }
        # validates score
        if ($ind_line[1] !~ /(1)|(0\.9[1-9]{1,3})/) {
            $error_count++;            
        }
        # validates target gene id
        if ($ind_line[2] !~ /((ENS\w{3}G|ENSG)\d{11})/) {
            $error_count++;
        }
        # validates position
        if ($ind_line[3] !~ /^(3'|5'|exon(\+)?|intron(\+)?)$/i) {
            $error_count++;        
        }
        # validates strand value
        if ($ind_line[4] !~ /(\+|\-)/) {
            $error_count++;   
        }
        # validates that no special characters are valid in description box
        if ($ind_line[5] =~ /[\'\"\,\\]/g) {
            $error_count++;
        }
        # if there are any errors from this line of file, push this line into error array
        if ($error_count != 0) {
            push @error_lines, join('', @ind_line);
        }
        # if no errors, make connection and insert into database
        else {
            my $dbh =DBI->connect("DBI:mysql:host=db-mysql;database=bif724_161a18", "bif724_161a18", $password) or die "Problem connecting" . DBI->errstr;
            # command for sql
            foreach(@ind_line){
                my $sql = "insert into a1_data values (?,?,?,?,?,?)";
                # prepares command
                my $sth = $dbh->prepare($sql) or die "problem with prepare" . DBI->errstr;
                $rows = $sth->execute($ind_line[0],$ind_line[1],$ind_line[2],$ind_line[3],$ind_line[4],$ind_line[5]);
                $success = 1
                }
                $dbh->disconnect() or die "Problem with disconnect" . DBI->errstr;
            }
        }
    # if there are no errors, redirect to the view program
    if (scalar(@error_lines) == 0) {
        print "Location: http://zenit.senecac.on.ca/~bif724_161a18/Assignment1/tash_a1_view.cgi?sort=new\n\n";
    }
    # prints the lines with errors
    else {
        print "Content-type: text/html\n\n";
        print begin_html("Upload a File", "tash_a1_add.css");
        foreach(@error_lines) {
            print "There is an error in this entry: $_<br>";
        }
    }
}
   
# file has not been selected, print form
else {
    print "Content-type: text/html\n\n";
    print begin_html("Upload a File", "tash_a1_add.css");
    print &form();
}

print end_html();

sub form() {
    #my $file_name = param('upload_file');
    #my $upload_fh = upload('upload_file');
    
    return<<FORM;
    <p>Manually entering each entry too tedious and time consuming? Look no further! Upload your CSV file here.</p>
    <form action="$0" method="post" enctype="multipart/form-data">
    <label class="upload">File to be uploaded: <input type="file" name="upload_file"><br/></label>
    <input type="submit">
    </form>
    
FORM

}


