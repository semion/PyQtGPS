import os

def main():
    ls = os.listdir(os.getcwd())
    
    for f in ls:
        fn, fend = f.split(".")
        try:
            z, x, y = fn.split("_")
            if z != "15":
                continue
            os.rename(f, "gm_%s_%s_%s.%s" % (x, y, z, fend))
            print f
        except:
            pass
        
        
if __name__ == "__main__":
    main()