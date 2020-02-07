#include "foo.h"
using namespace std;

int score(VAR *var, char **argv);

int main(int argc, char **argv)
{
	float final_score = 0;
	VAR *var = new VAR;
	read_fromfile(var, argv);
	final_score = score(var, argv);
	cout << final_score;
	return (0);
}

int score(VAR *var, char **argv)
{
	int **people;
	people = new int*[var->nDAY];
	for (int i = 0; i < var->nDAY; i++)
	{
		people[i] = new int[var->nT];
		for (int j = 0; j < var->nT; j++)
			people[i][j] = 0;
	}
	for (int i = 0; i < var->nEMPLOYEE; i++)
		for (int j = 0; j < var->nDAY; j++)
			for (int k = 0; k < var->nT; k++)
			{
				vector<int>::iterator it = find(var->phone.begin(), var->phone.end(), var->df_x[i][j]);
				if (it != var->phone.end())
					people[j][k] += var->A_t[var->df_x[i][j]][k];
			}
	
	int **output_people = new int*[var->nDAY];
	float lack = 0;
	float surplus = 0;
	float surplus_t = 0;
	for (int i = 0; i < var->nDAY; i++)
	{
		output_people[i] = new int[var->nT];
		for (int j = 0; j < var->nT; j++)
		{
			output_people[i][j] = people[i][j] - var->DEMAND[i][j];
			if (output_people[i][j] < 0)
				lack += -output_people[i][j];
			else if (output_people[i][j] > 0)
			{
				surplus_t = output_people[i][j];
				if (surplus_t > surplus)
					surplus = surplus_t;
			}
		}
	}
	
	float night = 0;
	float night_t = 0;
	for (int i = 0; i < var->nEMPLOYEE; i++)
	{
		if (var->nightdaylimit[i] > 0)
		{
			int count = 0;
			for (int j = 0; j < var->nDAY; j++)
			{
				vector<int>::iterator it = find(var->night.begin(), var->night.end(), var->df_x[i][j]);
				if (it != var->night.end())
					count++;
			}
			//cout << count << " " << var->nightdaylimit[i] << endl;
			night_t = count/var->nightdaylimit[i];
			if (night_t > night)
				night = night_t;
		}
	}

	int ***breakcount = new int**[var->nEMPLOYEE];
	for (int i = 0; i < var->nEMPLOYEE; i++)
	{
		breakcount[i] = new int*[var->nW];
		for (int j = 0; j < var->nW; j++)
		{
			breakcount[i][j] = new int[var->s_break.size()];
			for (int k = 0; k < var->s_break.size(); k++)
				breakcount[i][j][k] = 0;
		}
	}
	for (int i = 0; i < var->nEMPLOYEE; i++)
		for (int j = 0; j < var->nDAY; j++)
			for (int k = 0; k < var->s_break.size(); k++)
			{
				vector<int>::iterator it = find(var->s_break[k].begin(), var->s_break[k].end(), var->df_x[i][j]);
				if (it != var->s_break[k].end())
				{
					breakcount[i][var->WEEK_of_DAY[j]][k] = 1;
					break;
				}
			}
	float break_sum = 0;
	for (int i = 0; i < var->nEMPLOYEE; i++)
		for (int j = 0; j < var->nW; j++)
			for (int k = 0; k < var->s_break.size(); k++)
				break_sum += breakcount[i][j][k];
	
	float nooncount = 0;
	for (int i = 0; i < var->nEMPLOYEE; i++)
	{
		int count = 0;
		for (int j = 0; j < var->nDAY; j++)
		{
			vector<int>::iterator it = find(var->noon.begin(), var->noon.end(), var->df_x[i][j]);
			if (it != var->noon.end())
				count++;
		}
		if (count > nooncount)
			nooncount = count;
	}
	/*
	for (int i = 0; i < var->nDAY; i++)
	{
		for (int j = 0; j < var->nT; j++)
			cout << output_people[i][j] << " ";
		cout << endl;
	}
*/	
	//cout << lack << " " << surplus << " " << night << " " << break_sum << " " << nooncount << endl;
	float result = var->P0 * lack + var->P1 * surplus + var->P2 * night + var->P3 * break_sum + var->P4 * nooncount;
	return (result);
}
