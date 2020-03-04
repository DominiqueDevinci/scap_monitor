# Scap Monitor

This tool aims to monitor your system in real time to detect if your compliance level have changed.
Indeed, several tools provide "continously monitoring", but in fact the only "continous" aspect is the automatic update of SCAP content from upstream provider(s), and it can only schedules full scan on the local system.

So this software analyse your machine events in order to trigger only the related SCAP rules. It's embbed an XCCDF/OVAL parser which fetch rule trees and their related tests in order to know which rule can be affected by a given event; for instance, if you modify the file /etc/ssh/sshd_config, the rules which check ssh daemon configuration will be triggered (and Scap Monitor also keep an history of rule results in order to know if a rule result have changed). Example in a demonstration video: https://www.youtube.com/watch?v=Rw4tlCvYNhM

## Installation

You need to compile the lastest openscap version (branch maint-1.3) because it fixes a lot of oscap python binding issues. Then install libnotify2 if you want desktop notifications (`pip install notify2`), and run `python main.py --help`

## Integration

Scap Monitor sends events to syslog (and optionally notify with desktop popup), so the integration is really easy in an existing secured context (since secured context involve a good log monitoring). For instance you can use rsyslog to forward Scap Monitor logs to a centralized server.

**WARNING**: This software is just a proof of concept and isn't designed for a production env. It leveraging OpenSCAP python bindings which is unstable and suffering of memory leaks (and the software itself isn't optimized). In order to have a reliable production tool, this software should be re-written in C/C++ using directly oscap libraries instead of the python binding.

## Usage

usage: main.py [-h] [-v {DEBUG,INFO,WARNING,ALERT}] [-n] [--dpkg] [-c]

optional arguments:
  -h, --help            show this help message and exit
  -v {DEBUG,INFO,WARNING,ALERT}, --verbosity {DEBUG,INFO,WARNING,ALERT}
                        Verbosity level, corresponding to syslog priority.
  -n, --desktop-notify  Show desktop notifs with noticeable events .
  --dpkg                Show desktop notifs with noticeable events .
  -c, --change-only     Notify only when a rule result changes.


## To discuss

* Remediations: it should be great to be able to immediatly fix a new security compliance vulnerability, but it involves to have root privilege, and run this software (which leverage oscap) as root could be a high security flaw. However it can be possible to imaginate a remote daemon which take security measures when a suspicious event is detected, like degrading privileges on the machine, but this job doesn't depends of Scap Monitor (and isn't only related to Scap Monitor but also to all other security logs). To i've decided that's not the work ok Scap Daemon to do this, it's too dangerous and could be more dangerous than secured.

## TODO List

* General refactoring
* Build deb/rpm packages.
* Delayed queue system in order to handle the case when the same event is triggered several time in less than one second. This could also improve performance by evaluating several rules at the same time.
* Automatically fetch remote (and verified) SCAP content
* Tools that generate only a map betwwen oval tests and linked xccdf_rules (for a given benchmark / profile)
* Possibility to don't keep the benchmark loaded in memory, and to use oscap command line instead of internal python binding. This should be more reliable (almost eliminate segfault), and more optimized (no memory leak neither a huge benchmark loaded in memory). However, the delay of detection will be a little longer with this method.
