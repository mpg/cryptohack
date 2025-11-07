/* run with gp -q rsa_factoring.gp (after apt install pari-gp) */
n = 510143758735509025530880200653196460532653147;
f = factorint(n);
print(f);
quit();
